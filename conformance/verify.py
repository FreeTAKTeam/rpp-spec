# /// script
# requires-python = ">=3.10"
# dependencies = ["cbor2==6.3.0", "cryptography==50.0.2"]
# ///
"""Verify the released fixture corpus. Run with uv run conformance/verify.py."""
import io
import json
from hashlib import sha256
from pathlib import Path
from unittest import TestCase, main

import cbor2
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

VECTORS = json.loads((Path(__file__).resolve().parents[1] / "vectors/rc1.json").read_text())


def encode(value):
    return cbor2.dumps(value, canonical=True)


def diagnostic(value):
    if isinstance(value, str) and value.startswith("h'") and value.endswith("'"):
        return bytes.fromhex(value[2:-1])
    if isinstance(value, dict):
        return {int(k): diagnostic(v) for k, v in value.items()}
    if isinstance(value, list):
        return [diagnostic(v) for v in value]
    return value


def decode(payload):
    stream = io.BytesIO(payload)
    try:
        item = cbor2.load(stream, allow_duplicate_keys=False, allow_indefinite=False, max_depth=12)
    except cbor2.CBORDecodeError:
        return None, "malformed"
    if stream.read():
        return None, "malformed"
    if encode(item) != payload:
        return None, "noncanonical"
    return item, None


def resource_result(payload, plan, manifest, metadata, committed=None):
    if metadata != plan[22]:
        return "no_accepted_plan"
    if committed is not None:
        return "idempotent" if committed == payload else "conflicting_duplicate"
    if len(payload) != plan[20] or sha256(payload).digest() != plan[21]:
        return "invalid_bundle"
    offset = 0
    for index in plan[19]:
        chunk = manifest[32][index]
        end = offset + chunk[20]
        if sha256(payload[offset:end]).digest() != chunk[21]:
            return "chunk_mismatch"
        offset = end
    return "accept" if offset == len(payload) else "invalid_bundle"


def fixture_outcome(case, manifest, plan):
    payload = bytes.fromhex(case["input_hex"])
    if case["kind"] == "resource":
        if "plan" in case:
            plan = diagnostic(case["plan"]["value"])
        metadata = bytes.fromhex(case["metadata_hex"]) if "metadata_hex" in case else plan[22]
        committed = case.get("already_committed_payload_hex")
        return resource_result(payload, plan, manifest, metadata,
                               bytes.fromhex(committed) if committed is not None else None)

    item, error = decode(payload)
    if error:
        return error
    if item[1] != 3:
        return "unsupported_version"
    if item.get(11):
        return "unsupported_extension"
    if case["kind"] == "manifest":
        if sha256(payload).hexdigest() != case["expected_manifest_hash_hex"]:
            return "invalid_hash"
        signature = item.pop(7)
        key = bytes.fromhex(VECTORS["packages"]["one"]["publisher_public_hex"])
        try:
            Ed25519PublicKey.from_public_bytes(key[32:]).verify(signature, encode(item))
        except InvalidSignature:
            return "invalid_signature"
        return "accept"

    now = case.get("receive_time", VECTORS["fixture_time"])
    if not item[6] <= now < item[12] or not 1 <= item[12] - item[6] <= 300:
        return "expired"
    if item[0] == 7:
        peer_key = bytes.fromhex(case.get("identified_public_hex",
                                          VECTORS["packages"]["second_owner"]["publisher_public_hex"]))
        identity = sha256(peer_key).digest()[:16]
        name_hash = sha256(b"rpp.receive").digest()[:10]
        if sha256(name_hash + identity).digest()[:16] != item[5]:
            return "not_authorized"
        previous = -1
        for selection in item[23]:
            first, last = selection if isinstance(selection, list) else (selection, selection)
            if not previous < first <= last < manifest[24]:
                return "invalid_selection"
            previous = last
    if item[0] == 4 and item[20] > case["accepted_maximum"]:
        return "limit_exceeded"
    if item[0] == 6 and item[17] == 3:
        if item[24] != manifest[24] or case["verified_count"] != manifest[24] or item[23]:
            return "incomplete"
    return "accept"


class ReleaseVectors(TestCase):
    def test_encodings(self):
        def visit(node):
            if isinstance(node, dict):
                if "cbor_hex" in node:
                    self.assertEqual(encode(diagnostic(node["value"])).hex(), node["cbor_hex"])
                for child in node.values():
                    visit(child)
            elif isinstance(node, list):
                for child in node:
                    visit(child)
        visit(VECTORS)

    def test_manifests(self):
        for name, package in VECTORS["packages"].items():
            with self.subTest(name=name):
                manifest = diagnostic(package["value"])
                self.assertEqual(sha256(encode(manifest)).hexdigest(), package["manifest_hash_hex"])
                signature = manifest.pop(7)
                public = bytes.fromhex(package["publisher_public_hex"])
                Ed25519PublicKey.from_public_bytes(public[32:]).verify(signature, encode(manifest))
                package_id = manifest.pop(2)
                self.assertEqual(sha256(encode(manifest)).digest(), package_id)
                self.assertEqual(package_id.hex(), package["package_id_hex"])
                inventory = []
                logical_size = 0
                self.assertEqual(len(package["files"]), len(manifest[31]))
                for file, descriptor in zip(package["files"], manifest[31]):
                    chunks = [bytes.fromhex(c) for c in file["chunks_hex"]]
                    data = b"".join(chunks)
                    self.assertEqual(descriptor[40], file["path"])
                    self.assertEqual(descriptor[43], [len(inventory), len(chunks)])
                    self.assertEqual(descriptor[20], len(data))
                    self.assertEqual(descriptor[41], sha256(data).digest())
                    logical_size += len(data)
                    for chunk in chunks:
                        inventory.append({23: len(inventory), 20: len(chunk), 21: sha256(chunk).digest()})
                self.assertEqual(manifest[32], inventory)
                self.assertEqual(manifest[24], len(inventory))
                self.assertEqual(manifest[20], logical_size)

    def test_exchange(self):
        commands = {name: diagnostic(v["value"]) for name, v in VECTORS["commands"].items()}
        registry = ["Offer", "OfferAck", "ManifestRequest", "ResourcePlan",
                    "ResourceAccept", "TransferReceipt", "MissingChunks"]
        self.assertEqual({name: cmd[0] for name, cmd in commands.items()},
                         {name: i for i, name in enumerate(registry, 1)})
        package = VECTORS["packages"]["resume101"]
        manifest = diagnostic(package["value"])
        manifest_hash = bytes.fromhex(package["manifest_hash_hex"])
        receiver = bytes.fromhex(VECTORS["packages"]["second_owner"]["publisher_public_hex"])
        inbox = sha256(sha256(b"rpp.receive").digest()[:10] + sha256(receiver).digest()[:16]).digest()[:16]
        for cmd in commands.values():
            self.assertEqual((cmd[1], cmd[2], cmd[3], cmd[4], cmd[5]),
                             (3, manifest[2], manifest_hash, manifest[8], inbox))
        self.assertEqual(commands["Offer"][9], manifest[9])
        replies = {"Offer": "OfferAck", "MissingChunks": "ResourcePlan",
                   "ManifestRequest": None, "ResourceAccept": None, "TransferReceipt": None}
        self.assertEqual(set(VECTORS["results"]), set(replies))
        for request, reply in replies.items():
            cmd = commands[request]
            envelope = diagnostic(VECTORS["results"][request]["value"])
            expected = encode(commands[reply]) if reply else None
            self.assertEqual(envelope, [1, cmd[13], 0, None, expected])
            if reply:
                for key in (2, 3, 4, 5, 6, 12, 13):
                    self.assertEqual(cmd[key], commands[reply][key])
        self.assertEqual(commands["ResourcePlan"][22], commands["MissingChunks"][13])
        self.assertEqual(commands["ResourceAccept"][22], commands["ResourcePlan"][22])
        self.assertLessEqual(len(encode(manifest)), commands["ManifestRequest"][18])
        self.assertLessEqual(commands["ResourcePlan"][20], commands["MissingChunks"][18])

        public = bytes.fromhex(package["publisher_public_hex"])
        key = Ed25519PublicKey.from_public_bytes(public[32:])
        destinations = {"Package": manifest[8], "Manifest": manifest[9], "File": manifest[31][0][46]}
        for name, destination in destinations.items():
            version, obj, parent, iri, body, signature = diagnostic(VECTORS["resume_publication"][name]["value"])
            self.assertEqual((version, obj, parent), (1, destination, None))
            self.assertEqual(iri, "https://freetakteam.github.io/rpp/ontology#" + name)
            key.verify(signature, encode(["rdo.revision.v1", version, obj, parent, iri, body]))
            expected_body = {0: manifest[8], 1: manifest[9], 2: manifest[2], 3: manifest_hash}
            if name == "File":
                expected_body.update({4: manifest[31][0][41], 5: manifest[31][0][40]})
            self.assertEqual(body, expected_body)

    def test_outcomes(self):
        manifest = diagnostic(VECTORS["packages"]["resume101"]["value"])
        plan = diagnostic(VECTORS["commands"]["ResourcePlan"]["value"])
        for case in VECTORS["negative"]:
            with self.subTest(case=case["case"]):
                self.assertEqual(fixture_outcome(case, manifest, plan), case["expect"])
        for name, control in VECTORS["additional_controls"].items():
            with self.subTest(control=name):
                case = {"kind": "control", "input_hex": control["cbor_hex"]}
                self.assertEqual(fixture_outcome(case, manifest, plan), "accept")

    def test_resume(self):
        resume = VECTORS["resume"]
        package = diagnostic(VECTORS["packages"][resume["package"]]["value"])
        commands = {name: diagnostic(v["value"]) for name, v in VECTORS["commands"].items()}
        held = {i for first, last in resume["verified_before"] for i in range(first, last + 1)}
        missing = sorted(set(range(package[24])) - held)
        self.assertEqual(missing, commands["MissingChunks"][23])
        self.assertEqual(missing, commands["ResourcePlan"][19])
        self.assertEqual(missing, resume["missing"])
        data = bytes.fromhex(resume["payload_hex"])
        args = data, commands["ResourcePlan"], package, bytes.fromhex(resume["resource_metadata_value_hex"])
        self.assertEqual(resource_result(*args), "accept")
        self.assertEqual(resource_result(*args, committed=data), resume["repeat_identical_resource"])
        self.assertEqual(missing[1:], resume["after_interruption_with_only_17_committed"])
        receipt = commands[resume["expected_receipt"]]
        self.assertEqual((receipt[17], receipt[23], receipt[24]), (3, [], len(held) + len(missing)))


if __name__ == "__main__":
    main()
