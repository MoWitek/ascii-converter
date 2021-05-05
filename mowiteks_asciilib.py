from PIL import Image, ImageDraw, ImageFile
import curses
import time
import cv2
import os
ImageFile.LOAD_TRUNCATED_IMAGES = True

class core:
    def __init__(
            self,
            algorithm: str = "u",

            pixels: list = list(" .,~:;irsXA253hMHGS#9B&@"),

            height: int = 80,
            aspect_ratio: int = 16 / 9,
            fixed_sides: tuple = None,
            image_file: str = "img.jpg",
    ):
        self.algorithm = algorithm
        self.pixels = pixels[::-1]  # invert color range
        self.image_file = image_file
        self.height = height
        self.aspect_ratio = aspect_ratio
        self.fixed_sides = fixed_sides

    def convert_to_ascii(self,
                         file: str = None,
                         aspectratio: int = None,
                         default_aspect: bool = False,
                         algorithm: str = None
                         ):
        if file is not None:
            img = Image.open(file)
        else:
            img = Image.open(self.image_file)
        img = img.convert("L")  # convert to greyscale

        if aspectratio is None:
            aspectratio = self.aspect_ratio

        if algorithm is None:
            algorithm = self.algorithm

        (x, y) = img.size
        if not default_aspect:
            if self.fixed_sides is None:
                newsize = (int(x / y * self.height * aspectratio), self.height)
            else:
                newsize = self.fixed_sides
        else:
            newsize = (int(x / y * self.height), self.height)

        img = img.resize(newsize, Image.ANTIALIAS)

        out = ""
        if algorithm == "s-s":
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    out += self.pixels[((255 - img.getpixel((x, y))) // 24)]  # 24 pixels per tonal range
                    out += " "
                out += "\n"

        elif algorithm == "u-s":
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    out += self.pixels[round((255 - img.getpixel((x, y))) // (256 / (len(self.pixels))))]
                    out += " "
                out += "\n"

        elif algorithm == "s":
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    out += self.pixels[((255 - img.getpixel((x, y))) // 24)]  # 24 pixels per tonal range
                out += "\n"

        elif algorithm == "u":
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    out += self.pixels[round((255 - img.getpixel((x, y))) // (256 / (len(self.pixels))))]
                out += "\n"

        return out

    def render_img(self, in_filename, out_filename,
                   background_color: tuple = (0, 0, 0),
                   text_color: tuple = (255, 255, 255)
                   ):
        # constants
        letter_width = 6
        letter_height = 12
        line_space = 3

        text_content = self.convert_to_ascii(in_filename, default_aspect=True, algorithm="u-s")
        text_spliced = text_content.split("\n")
        # the 2 balances out the start at 1 1
        size = len(text_spliced[0]) * letter_width + 2, len(text_spliced) * letter_height + 2
        img = Image.new('RGB', size, color=background_color)

        d = ImageDraw.Draw(img)
        # d.text((1, 1), text_content, fill=text_color)

        line = 1
        for ts in text_spliced:
            d.text((1, line), ts, fill=text_color)
            line += 12
        img.save(out_filename)

    def render_frames(
            self,
            import_folder: str = "frames",
            export_folder: str = "export"
    ):
        try:
            os.mkdir(export_folder)
        except:
            pass
        imag_c = [img for img in os.listdir(import_folder) if img.endswith(".jpg") or img.endswith(".png")][::-1]
        images = []
        for c in range(len(imag_c)):
            images.append(f"{import_folder}/frame{c}.jpg")

        c = -1
        for img in images:
            c += 1
            self.render_img(img, f"{export_folder}/export{c}.jpg")
            print(f"Rendering Frame: {c}")

    def stick_frames_old(self, video_name: str = "export-video.avi", image_folder: str = "export", framerate: int = 30):
        imag_c = [img for img in os.listdir(image_folder) if img.endswith(".jpg") or img.endswith(".png")][::-1]

        images = []
        for c in range(len(imag_c)):
            images.append(f"{image_folder}/export{c}.jpg")

        frame = cv2.imread(images[0])
        height, width, layers = frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video = cv2.VideoWriter(video_name, fourcc, framerate, (width, height))

        for image in images:
            video.write(cv2.imread(image))

        video.release()

    def stick_frames(self, video_name: str = "export-video.avi", image_folder: str = "export", framerate: int = 30):
        imag_c = [img for img in os.listdir(image_folder) if img.endswith(".jpg")][::-1]

        f = open("images.txt", "w")
        f.write("")
        f.close()

        f = open("images.txt", "a")
        for c in range(len(imag_c)):
            f.write(f"file {image_folder}/export{c}.jpg\n")
        f.close()

        os.system(f"ffmpeg -r {framerate} -y -loglevel panic -f concat -i images.txt -c:v libx264 -pix_fmt yuv420p {video_name}")

    def extract_frames(self, file: str, folder: str = "frames"):
        try:
            os.mkdir(folder)
        except:
            pass

        vidcap = cv2.VideoCapture(file)
        success, image = vidcap.read()
        count = 0
        while success:
            cv2.imwrite(f"{folder}/frame{count}.jpg", image)  # save frame as JPEG file
            success, image = vidcap.read()
            count += 1

    def extract_audio(self,
                      import_video_file: str,
                      export_audio_file: str = "output-audio.mp3"):
        # os.system(f"ffmpeg -i {import_video_file} -vn -acodec copy {export_audio_file}")
        os.system(f"ffmpeg -i {import_video_file} -y -loglevel panic -q:a 0 -map a {export_audio_file}")

    def add_audio(self,
                  import_video: str = "export-video.avi",
                  import_audio: str = "output-audio.mp3",
                  export_combined: str = "_with-audio.avi"
                  ):
        os.system(f"ffmpeg -i {import_video} -i {import_audio} -y -loglevel panic -c copy -map 0:v:0 -map 1:a:0 {export_combined}")

    def sync_audio(self,
                   in_file: str = "_with-audio.avi",
                   offset: str = "0.1",
                   out_file: str = "final.avi"):

        os.system(f"ffmpeg -i {in_file} -itsoffset {offset} -i {in_file} -y -loglevel panic -map 1:v -map 0:a  -c copy {out_file}")

    def clean_up(self, *args):
        for a in args:
            try:
                os.remove(a)
            except:
                pass

    def render_video(self, video_in: str, video_out: str = "output.avi"):
        timer_start = time.time()
        in_file = video_in
        temporary_file = "video-only.avi"
        temporary_file2 = "unsynced-audio.avi"
        out_file = video_out
        audio_file = "audio-only.mp3"

        fps = cv2.VideoCapture(video_in).get(cv2.CAP_PROP_FPS)

        print("Extracting Frames...")
        self.extract_frames(in_file)
        print("Extracting Audio...")
        self.extract_audio(in_file, audio_file)
        print("Rendering Frames...")
        self.render_frames()
        print("Sticking Frames Toghther...")
        self.stick_frames(temporary_file, framerate=fps)
        print("Adding Audio to Video...")
        self.add_audio(temporary_file, audio_file, temporary_file2)
        print("Syncing Audio...")
        self.sync_audio(temporary_file2, "0", out_file)
        print("Cleaning up...")
        self.clean_up(temporary_file, temporary_file2, audio_file)
        print("Done!")

        print("Took:", time.time() - timer_start)

    def make_pic(self, camera):
        return_value, image = camera.read()
        cv2.imwrite(str(self.image_file), image)

    def live(self):
        self.display_stats()

    def display_stats(self):
        stdscr = curses.initscr()

        camera_port = 0
        camera = cv2.VideoCapture(camera_port, cv2.CAP_DSHOW)
        time.sleep(0.1)

        avg_frame_time = 0
        avg_fps = 0

        frames = 0
        while True:
            self.make_pic(camera)

            timer = time.time()
            out = self.convert_to_ascii()

            avg_frame_time += time.time() - timer
            avg_fps += 1 / (time.time() - timer)
            frames += 1

            stdscr.clear()
            try:
                # stdscr.addstr(f"[NOW Frame Time] {time.time() - timer}\n[AVG Frame Time] {avg_frame_time /
                # frames}\n[NOW FPS] {1 / (time.time() - timer)}\n[AVG FPS] {avg_fps / frames}\n")
                stdscr.addstr(out)
            except curses.error:
                pass

            stdscr.refresh()
