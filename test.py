import eddsa_signer
from pydub import AudioSegment
import time, sys

length = [100, 1000, 60 * 1000]
trials = 5

def main():
    audio_signer = eddsa_signer.AudioSigner()
    audio_signer.import_keys(signing_key_path="sk.pri", verifying_key_path="vk.pub")

    input_audio = AudioSegment.from_file('test.wav', format='wav')
    length.append(len(input_audio))

    for l in length:
        sliced_audio = input_audio[:l]
        sliced_audio.export('test_{}.wav'.format(l), format='wav')

    # Control
    print("===CONTROL===")
    for l in length:
        duration_sign = []
        duration_verify = []
        is_valid = True
        for _ in range(0, trials):
            start_t = time.process_time()
            audio_signer.sign('test_{}.wav'.format(l), 'test_{}_encoded.wav'.format(l))
            duration = (time.process_time() - start_t) * 1000
            if (duration != 0):
                duration_sign.append(duration)
            
            start_t = time.process_time()
            is_valid &= audio_signer.verify('test_{}_encoded.wav'.format(l))
            duration = (time.process_time() - start_t) * 1000
            if (duration != 0):
                duration_verify.append(duration)
        
        if duration_sign == []:
            duration_sign = [0]
        if duration_verify == []:
            duration_verify = [0]

        print('Audio length: {}'.format(l))
        print('Valid: {}'.format(is_valid))
        print('Execution time (sign): {} ms'.format(sum(duration_sign)/float(len(duration_sign))))
        print('Execution time (verify): {} ms'.format(sum(duration_verify)/float(len(duration_verify))))

    # Modified Key
    print("\n===MODIFIED KEY===")
    audio_signer.import_keys(verifying_key_path="vk2.pub")
    for l in length:
        duration_sign = []
        duration_verify = []
        is_valid = True
        for _ in range(0, trials):
            start_t = time.process_time()
            audio_signer.sign('test_{}.wav'.format(l), 'test_{}_encoded.wav'.format(l))
            duration = (time.process_time() - start_t) * 1000
            if (duration != 0):
                duration_sign.append(duration)
            
            start_t = time.process_time()
            is_valid &= audio_signer.verify('test_{}_encoded.wav'.format(l))
            duration = (time.process_time() - start_t) * 1000
            if (duration != 0):
                duration_verify.append(duration)
        
        if duration_sign == []:
            duration_sign = [0]
        if duration_verify == []:
            duration_verify = [0]

        print('Audio length: {}'.format(l))
        print('Valid: {}'.format(is_valid))
        print('Execution time (sign): {} ms'.format(sum(duration_sign)/float(len(duration_sign))))
        print('Execution time (verify): {} ms'.format(sum(duration_verify)/float(len(duration_verify))))

    # Modified Data
    print("\n===MODIFIED DATA===")
    audio_signer.import_keys(verifying_key_path="vk.pub")
    for l in length:
        duration_sign = []
        duration_verify = []
        is_valid = True
        for _ in range(0, trials):
            start_t = time.process_time()
            audio_signer.sign('test_{}.wav'.format(l), 'test_{}_encoded.wav'.format(l))
            duration = (time.process_time() - start_t) * 1000
            if (duration != 0):
                duration_sign.append(duration)
            
            input_audio = AudioSegment.from_file('test_{}_encoded.wav'.format(l), format='wav')
            audio_data = bytearray(input_audio.raw_data)
            audio_data[0] &= 0b00000001
            AudioSegment(
                data=bytes(audio_data),
                sample_width=input_audio.sample_width,
                channels=input_audio.channels,
                frame_rate=input_audio.frame_rate
            ).export('test_{}_encoded.wav'.format(l), format='wav')
            
            start_t = time.process_time()
            is_valid &= audio_signer.verify('test_{}_encoded.wav'.format(l))
            duration = (time.process_time() - start_t) * 1000
            if (duration != 0):
                duration_verify.append(duration)
        
        if duration_sign == []:
            duration_sign = [0]
        if duration_verify == []:
            duration_verify = [0]

        print('Audio length: {}'.format(l))
        print('Valid: {}'.format(is_valid))
        print('Execution time (sign): {} ms'.format(sum(duration_sign)/float(len(duration_sign))))
        print('Execution time (verify): {} ms'.format(sum(duration_verify)/float(len(duration_verify))))

    # Modified Data
    print("\n===MODIFIED SIGNATURE===")
    audio_signer.import_keys(verifying_key_path="vk.pub")
    for l in length:
        duration_sign = []
        duration_verify = []
        is_valid = True
        for _ in range(0, trials):
            start_t = time.process_time()
            audio_signer.sign('test_{}.wav'.format(l), 'test_{}_encoded.wav'.format(l))
            duration = (time.process_time() - start_t) * 1000
            if (duration != 0):
                duration_sign.append(duration)
            
            input_audio = AudioSegment.from_file('test_{}_encoded.wav'.format(l), format='wav')
            audio_data = bytearray(input_audio.raw_data)
            index = 0
            if sys.byteorder == 'big':
                index = input_audio.sample_width - 1
            if audio_data[index] % 2 == 0:
                audio_data[index] &= 0b11111111
            else:
                audio_data[index] &= 0b11111110
                
            AudioSegment(
                data=bytes(audio_data),
                sample_width=input_audio.sample_width,
                channels=input_audio.channels,
                frame_rate=input_audio.frame_rate
            ).export('test_{}_encoded.wav'.format(l), format='wav')
            
            start_t = time.process_time()
            is_valid &= audio_signer.verify('test_{}_encoded.wav'.format(l))
            duration = (time.process_time() - start_t) * 1000
            if (duration != 0):
                duration_verify.append(duration)
        
        if duration_sign == []:
            duration_sign = [0]
        if duration_verify == []:
            duration_verify = [0]

        print('Audio length: {}'.format(l))
        print('Valid: {}'.format(is_valid))
        print('Execution time (sign): {} ms'.format(sum(duration_sign)/float(len(duration_sign))))
        print('Execution time (verify): {} ms'.format(sum(duration_verify)/float(len(duration_verify))))




if __name__ == "__main__":
    main()