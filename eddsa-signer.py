import ed25519
from lsb_steganography import AudioLSB


class AudioSigner:
    lsb_normalizer = bytes([0] * 64)

    def generate_keys(self):
        self.signing_key, self.verifying_key = ed25519.create_keypair()

    def export_keys(self, signing_key_path=None, verifying_key_path=None):
        if signing_key_path is not None:
            open(signing_key_path, 'wb').write(self.signing_key.to_bytes())

        if verifying_key_path is not None:
            open(verifying_key_path, 'wb').write(self.verifying_key.to_bytes())

    def set_keys(self, signing_key=None, verifying_key=None):
        if signing_key is not None:
            self.signing_key = signing_key

        if verifying_key is not None:
            self.verifying_key = verifying_key

    def import_keys(self, signing_key_path=None, verifying_key_path=None):
        signing_key = None
        verifying_key = None

        if signing_key_path is not None:
            keydata = open(signing_key_path, 'rb').read()
            signing_key = ed25519.SigningKey(keydata)

        if verifying_key_path is not None:
            keydata = open(verifying_key_path, 'rb').read()
            verifying_key = ed25519.SigningKey(keydata)

        self.set_keys(signing_key=signing_key, verifying_key=verifying_key)

    def sign(self, input_path, output_path):
        audio_lsb = AudioLSB(input_path)
        audio_lsb.encode(self.lsb_normalizer)

        signature = self.signing_key.sign(bytes(audio_lsb.audio_data))
        audio_lsb.encode(signature)

        audio_lsb.export(output_path)

    def verify(self, input_path):
        audio_lsb = AudioLSB(input_path)
        signature = audio_lsb.decode(length=64)

        audio_lsb.encode(self.lsb_normalizer)
        try:
            self.verifying_key.verify(signature, audio_lsb.audio_data)
            return True
        except ed25519.BadSignatureError:
            return False

def main():
    print('Hello')


if __name__ == "__main__":
    main()
