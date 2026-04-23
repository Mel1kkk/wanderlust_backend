from hashlib import sha256

class Hasher:
    def hash_it(text_to_hash: str) -> str:
        return sha256(text_to_hash.encode()).hexdigest()