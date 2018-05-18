import ed25519
from lsb_steganography import AudioLSB
import math
from gmpy2 import divm

class AudioSigner:
    lsb_normalizer = bytes([0] * 64)

    def generate_keys(self):
        self.signing_key, self.verifying_key = ed25519.create_keypair()

    def export_keys(self, signing_key_path=None, verifying_key_path=None):
        if signing_key_path is not None:
            open(signing_key_path, 'wb').write(self.signing_key.to_seed())
            print("Signing key seed: %d" % int.from_bytes(self.signing_key.to_seed(), byteorder='little'))
            print("Signing key seed: ", self.signing_key.to_ascii(encoding='base64'))

        if verifying_key_path is not None:
            open(verifying_key_path, 'wb').write(self.verifying_key.to_bytes())
            vk = self.verifying_key.to_bytes()
            print("Verifying key: ", self.verifying_key.to_ascii(encoding='base64'))
            print("Verifying key: %d" % int.from_bytes(vk, byteorder='little'))
            parity = vk[-1] >> 7
            print("Parity bit: %d" % parity)
            y = bytearray(vk)
            y[-1] &= 0b01111111
            y = int.from_bytes(bytes(y), byteorder='little')
            print("Actual y value: %d" % y)
            d = 37095705934669439343138083508754565189542113879843219016388785533085940283555
            p = pow(2, 255) - 19
            x = math.sqrt(divm((y ** 2 - 1), ((d * y) ** 2 + 1), p))
            if parity == 1:
                x *= -1
            print("Actual x value: %d" % x)

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
            verifying_key = ed25519.VerifyingKey(keydata)

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
            self.verifying_key.verify(signature, bytes(audio_lsb.audio_data))
            return True
        except ed25519.BadSignatureError:
            return False


def _main_generate_keys(args):
    audio_signer = AudioSigner()
    audio_signer.generate_keys()
    audio_signer.export_keys(
        signing_key_path=args.signing_key_path, verifying_key_path=args.verifying_key_path)


def _main_sign(args):
    audio_signer = AudioSigner()
    audio_signer.import_keys(signing_key_path=args.signing_key_path)
    audio_signer.sign(args.input_path, args.output_path)


def _main_verify(args):
    audio_signer = AudioSigner()
    audio_signer.import_keys(verifying_key_path=args.verifying_key_path)
    print(audio_signer.verify(args.input_path))


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Lossless audio EdDSA digital signer')
    subparsers = parser.add_subparsers(help='Commands')

    # Generate keys
    keys_parser = subparsers.add_parser('keys', help='Key generation')
    keys_parser.add_argument(
        '-sk', action='store', dest='signing_key_path', help='Signing key output path')
    keys_parser.add_argument(
        '-vk', action='store', dest='verifying_key_path', help='Verifying key output path')
    keys_parser.set_defaults(func=_main_generate_keys)

    # Sign
    sign_parser = subparsers.add_parser('sign', help='Audio signing')
    sign_parser.add_argument('-i', action='store',
                             dest='input_path', help='Audio input path')
    sign_parser.add_argument('-o', action='store',
                             dest='output_path', help='Audio output path')
    sign_parser.add_argument(
        '-sk', action='store', dest='signing_key_path', help='Signing key input path')
    sign_parser.set_defaults(func=_main_sign)

    # Verify
    verify_parser = subparsers.add_parser('verify', help='Audio verification')
    verify_parser.add_argument(
        '-i', action='store', dest='input_path', help='Audio input path')
    verify_parser.add_argument(
        '-vk', action='store', dest='verifying_key_path', help='Verifying key input path')
    verify_parser.set_defaults(func=_main_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
