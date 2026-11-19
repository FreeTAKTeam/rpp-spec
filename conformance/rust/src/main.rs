//! Independent encoder for the published RC1 vectors. Inputs are checked-in fixture data.
use ciborium::value::Value as Cbor;
use ed25519_dalek::{Signer, SigningKey};
use serde_json::Value as Json;
use sha2::{Digest, Sha256};

fn bytes(value: &Json) -> Vec<u8> {
    hex::decode(value.as_str().expect("fixture hex string")).expect("valid fixture hex")
}

fn diagnostic(value: &Json) -> Cbor {
    match value {
        Json::Null => Cbor::Null,
        Json::Number(n) => Cbor::Integer(n.as_u64().expect("unsigned integer").into()),
        Json::String(s) => match s.strip_prefix("h'").and_then(|x| x.strip_suffix('\'')) {
            Some(hex) => Cbor::Bytes(hex::decode(hex).expect("byte string")),
            None => Cbor::Text(s.clone()),
        },
        Json::Array(items) => Cbor::Array(items.iter().map(diagnostic).collect()),
        Json::Object(map) => {
            let mut entries: Vec<_> = map
                .iter()
                .map(|(k, v)| (k.parse::<u64>().expect("integer key"), diagnostic(v)))
                .collect();
            entries.sort_by_key(|(k, _)| *k);
            Cbor::Map(
                entries
                    .into_iter()
                    .map(|(k, v)| (Cbor::Integer(k.into()), v))
                    .collect(),
            )
        }
        _ => panic!("unsupported diagnostic value {value}"),
    }
}

fn encode(value: &Json) -> Vec<u8> {
    let mut out = Vec::new();
    ciborium::ser::into_writer(&diagnostic(value), &mut out).unwrap();
    out
}

fn check_samples(node: &Json) {
    match node {
        Json::Object(map) => {
            if let Some(expected) = map.get("cbor_hex") {
                assert_eq!(encode(&node["value"]), bytes(expected));
            }
            map.values().for_each(check_samples);
        }
        Json::Array(items) => items.iter().for_each(check_samples),
        _ => {}
    }
}

fn main() {
    let vectors: Json = serde_json::from_str(include_str!("../../../vectors/rc1.json")).unwrap();
    check_samples(&vectors);
    let publisher_keys: Vec<_> = [
        "fixture_identity_private_hex",
        "second_fixture_identity_private_hex",
    ]
    .iter()
    .map(|key| {
        let identity = bytes(&vectors[key]);
        SigningKey::from_bytes(identity[32..].try_into().unwrap())
    })
    .collect();
    for (name, package) in vectors["packages"].as_object().unwrap() {
        let mut manifest = package["value"].clone();
        assert_eq!(
            hex::encode(Sha256::digest(encode(&manifest))),
            package["manifest_hash_hex"],
            "{name}"
        );
        let signature = manifest.as_object_mut().unwrap().remove("7").unwrap();
        let public = bytes(&package["publisher_public_hex"]);
        let signer = publisher_keys
            .iter()
            .find(|key| key.verifying_key().as_bytes() == &public[32..])
            .expect("fixture publisher");
        assert_eq!(
            diagnostic(&signature),
            Cbor::Bytes(signer.sign(&encode(&manifest)).to_bytes().to_vec())
        );
        let package_id = manifest.as_object_mut().unwrap().remove("2").unwrap();
        let digest = Sha256::digest(encode(&manifest));
        assert_eq!(diagnostic(&package_id), Cbor::Bytes(digest.to_vec()));
        assert_eq!(hex::encode(digest), package["package_id_hex"], "{name}");
    }
    println!("RC1 fixture bytes, package IDs, signatures and manifest hashes match.");
}
