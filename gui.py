from threading import Thread
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import cv2 as cv
from PIL import Image, ImageTk


class SubtitleExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._create_layout()
        self.video_paths = None
        self.current_frame = None

    def _create_layout(self):
        self.root.title("Video Subtitle Extractor")

        self._menu_bar()

        self.main_frame = ttk.Frame(self.root, padding=(5, 5, 5, 15))

        self._video_frame()
        self._work_frame()
        self._output_frame()

        self.main_frame.grid(sticky="N, S, E, W")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def _menu_bar(self):
        self.root.option_add('*tearOff', FALSE)

        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        menu_file = Menu(menubar)
        menu_settings = Menu(menubar)

        menubar.add_cascade(menu=menu_file, label="File")
        menubar.add_cascade(menu=menu_settings, label="Settings")

        menu_file.add_command(label="Open", command=self._open_files)
        menu_file.add_command(label="Close", command=self._on_closing)

        menu_settings.add_command(label="Language", command=self._language_settings)
        menu_settings.add_command(label="Extraction", command=self._extraction_settings)

    def _video_frame(self):
        video_frame = ttk.Frame(self.main_frame)
        video_frame.grid(sticky="N, S, E, W")

        self.video_canvas = Canvas(video_frame, bg="black")
        self.video_canvas.grid()

        video_frame.grid_columnconfigure(0, weight=1)
        video_frame.grid_rowconfigure(0, weight=1)

    def _work_frame(self):
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.grid(row=1, sticky="N, S, E, W")

        self.run_button = ttk.Button(progress_frame, text="Run", command=self._run)
        self.run_button.grid(pady=10, padx=30)

        self.progress_bar = ttk.Progressbar(progress_frame, orient=HORIZONTAL, length=700, mode='determinate')
        self.progress_bar.grid(column=2, row=0)

    def _output_frame(self):
        output_frame = ttk.Frame(self.main_frame)
        output_frame.grid(row=2, sticky="N, S, E, W")

        self.text_output_widget = Text(output_frame, height=12, state="disabled")
        self.text_output_widget.grid(sticky="N, S, E, W")

        output_scroll = ttk.Scrollbar(output_frame, orient=VERTICAL, command=self.text_output_widget.yview)
        output_scroll.grid(column=1, row=0, sticky="N,S")

        self.text_output_widget.configure(yscrollcommand=output_scroll.set)

        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)

    def _language_settings(self):
        pass

    def _extraction_settings(self):
        pass

    def video_stream(self):
        while self.capture.isOpened():
            success, frame = self.capture.read()
            if not success:
                print(f"Video has ended!")
                break
            cv2image = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            self.current_frame = ImageTk.PhotoImage(image=img)
            self.video_canvas.create_image(0, 0, image=self.current_frame, anchor='center')

    def _display_video(self):
        if len(self.video_paths) == 1:
            for video in self.video_paths:
                self.video_paths = video
            self.capture = cv.VideoCapture(str(self.video_paths))
            width = int(self.capture.get(cv.CAP_PROP_FRAME_WIDTH))
            height = int(self.capture.get(cv.CAP_PROP_FRAME_HEIGHT))
            self.video_canvas.configure(width=width*0.5, height=height*0.5)

            Thread(target=self.video_stream, daemon=True).start()
        else:
            self._add_batch_mode_layout()

    def _open_files(self):
        title = "Open"
        file_types = (("mp4", "*.mp4"), ("mkv", "*.mkv"), ("All files", "*.*"))
        filenames = filedialog.askopenfilenames(title=title, filetypes=file_types)
        if filenames:
            for filename in filenames:
                self.write_to_output(f"Opened file: {filename}")
            self.video_paths = filenames
            self._display_video()

    def _add_batch_mode_layout(self):
        pass

    def _on_closing(self):
        self._stop_run()
        self.root.quit()
        self.capture.release()

    def _stop_run(self):
        self.interrupt = True
        self.run_button.configure(text="Run", command=self._run)

    def write_to_output(self, text):
        self.text_output_widget.configure(state="normal")
        self.text_output_widget.insert("end", f"{text}\n")
        self.text_output_widget.see("end")
        self.text_output_widget.configure(state="disabled")

    def long_running_method(self, count=0):
        num = 1000
        self.progress_bar.configure(maximum=num)
        if self.interrupt:
            return
        self.write_to_output(f"Line {count} of {num}")
        self.progress_bar['value'] += 1
        if count == num:
            self._stop_run()
            return
        self.root.after(1, lambda: self.long_running_method(count + 1))

    def _run(self):
        if self.video_paths:
            self.interrupt = False
            self.run_button.configure(text='Stop', command=self._stop_run)
            self.progress_bar['value'] = 0

            # self.long_running_method()
        else:
            self.write_to_output("No video has been selected!")


if __name__ == '__main__':
    rt = Tk()
    SubtitleExtractorGUI(rt)
    rt.mainloop()
