import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

APP_TITLE = "Pindahin File RAW by.onokpicture"
APP_VERSION = "4.0.0"
APP_AUTHOR = "onokpicture"

# ============================================================
# FORMAT RAW KAMERA
# ============================================================
RAW_EXTENSIONS = {
    # Sony
    ".arw",

    # Canon
    ".crw",
    ".cr2",
    ".cr3",

    # Nikon
    ".nef",
    ".nrw",

    # Fujifilm
    ".raf",

    # Panasonic / Lumix
    ".rw2",

    # Olympus / OM System
    ".orf",
    ".ori",

    # Pentax
    ".pef",

    # Samsung
    ".srw",

    # Leica
    ".rwl",

    # Hasselblad
    ".3fr",
    ".fff",

    # Phase One
    ".iiq",

    # Adobe / Universal RAW
    ".dng",

    # Generic RAW
    ".raw",

    # Mamiya
    ".mef",

    # Minolta
    ".mrw",

    # Epson
    ".erf",

    # Kodak
    ".kdc",
    ".dcr",

    # Sigma
    ".x3f",

    # Casio
    ".bay",

    # Pentax / Ricoh variants
    ".ptx",

    # Digital Back / Medium Format
    ".mos",
    ".mdc",

    # Various RAW formats
    ".cap",
    ".cine",
    ".iiq",
    ".pxn",
    ".rwz",
    ".sr2",
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
}


def extract_number(filename):
    """
    Mengambil nomor foto dari nama file.

    Prioritas:
    1. Nomor di dalam tanda kurung
       Contoh: A (123).ARW -> 123

    2. Angka terakhir pada nama file
       Contoh: DSC00123.ARW -> 123
    """

    stem = Path(filename).stem

    # Prioritas nomor dalam (...)
    matches = re.findall(r"\(\s*(\d+)\s*\)", stem)

    if matches:
        return int(matches[-1])

    # Kalau tidak ada (...), ambil angka terakhir
    matches = re.findall(r"(\d+)", stem)

    if matches:
        return int(matches[-1])

    return None


class App:

    def __init__(self, root):

        self.root = root

        self.root.title(APP_TITLE)

        self.root.geometry("780x620")

        self.root.minsize(720, 560)

        self.source_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.numbers_var = tk.StringVar()
        self.readonly_var = tk.BooleanVar(value=False)

        self.build_ui()

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        title = ttk.Label(
            self.root,
            text="Pindahin File RAW by.onokpicture",
            font=("Segoe UI", 20, "bold")
        )

        title.pack(
            anchor="w",
            padx=18,
            pady=(16, 2)
        )

        subtitle = ttk.Label(
            self.root,
            text=(
                "Pilih folder induk → semua subfolder otomatis discan. "
                "RAW diprioritaskan, jika tidak ada baru JPG/JPEG. • by.onokpicture"
            ),
            font=("Segoe UI", 10)
        )

        subtitle.pack(
            anchor="w",
            padx=18,
            pady=(0, 12)
        )

        frame = ttk.Frame(self.root)

        frame.pack(
            fill="x",
            padx=12
        )

        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        ttk.Label(
            frame,
            text="1. Folder induk RAW/JPG:",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=12,
            pady=(7, 3)
        )

        ttk.Entry(
            frame,
            textvariable=self.source_var
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=4
        )

        ttk.Button(
            frame,
            text="Pilih Folder",
            command=self.choose_source
        ).grid(
            row=1,
            column=1,
            padx=12,
            pady=4
        )

        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        ttk.Label(
            frame,
            text="2. Folder tujuan SELECTED:",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=12,
            pady=(9, 3)
        )

        ttk.Entry(
            frame,
            textvariable=self.output_var
        ).grid(
            row=3,
            column=0,
            sticky="ew",
            padx=12,
            pady=4
        )

        ttk.Button(
            frame,
            text="Pilih Folder",
            command=self.choose_output
        ).grid(
            row=3,
            column=1,
            padx=12,
            pady=4
        )

        # ----------------------------------------------------
        # NOMOR FOTO
        # ----------------------------------------------------

        ttk.Label(
            frame,
            text="3. Nama file / nomor foto pilihan client:",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=4,
            column=0,
            sticky="w",
            padx=12,
            pady=(9, 3)
        )

        ttk.Entry(
            frame,
            textvariable=self.numbers_var,
            font=("Consolas", 11)
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
            pady=4
        )

        ttk.Label(
            frame,
            text=(
                "Bisa paste langsung dari WhatsApp/Excel: SAD06736.JPG, "
                "1. SAD06764.JPG, bullet, koma, spasi, tab, atau enter."
            ),
            foreground="#666666"
        ).grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="w",
            padx=12,
            pady=(0, 7)
        )

        # ----------------------------------------------------
        # READ ONLY
        # ----------------------------------------------------

        ttk.Checkbutton(
            frame,
            text="Set file hasil menjadi Read-only setelah dipindahkan",
            variable=self.readonly_var
        ).grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="w",
            padx=12,
            pady=5
        )

        frame.columnconfigure(
            0,
            weight=1
        )

        # ----------------------------------------------------
        # BUTTON
        # ----------------------------------------------------

        buttons = ttk.Frame(self.root)

        buttons.pack(
            fill="x",
            padx=18,
            pady=10
        )

        ttk.Button(
            buttons,
            text="CARI & PINDAHKAN FILE",
            command=self.process
        ).pack(
            side="left"
        )

        ttk.Button(
            buttons,
            text="Bersihkan",
            command=self.clear
        ).pack(
            side="left",
            padx=8
        )

        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        log_frame = ttk.LabelFrame(
            self.root,
            text="Hasil proses"
        )

        log_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(2, 18)
        )

        self.log = tk.Text(
            log_frame,
            wrap="word",
            font=("Consolas", 10),
            state="disabled"
        )

        self.log.pack(
            side="left",
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        scrollbar = ttk.Scrollbar(
            log_frame,
            command=self.log.yview
        )

        scrollbar.pack(
            side="right",
            fill="y",
            pady=8
        )

        self.log.configure(
            yscrollcommand=scrollbar.set
        )

    # ========================================================
    # FOLDER
    # ========================================================

    def choose_source(self):

        folder = filedialog.askdirectory(
            title="Pilih folder induk RAW/JPG"
        )

        if folder:

            self.source_var.set(folder)

            if not self.output_var.get():

                self.output_var.set(
                    str(Path(folder) / "SELECTED")
                )

    def choose_output(self):

        folder = filedialog.askdirectory(
            title="Pilih folder tujuan SELECTED"
        )

        if folder:

            self.output_var.set(folder)

    # ========================================================
    # LOG
    # ========================================================

    def write_log(self, text):

        self.log.configure(
            state="normal"
        )

        self.log.insert(
            "end",
            text + "\n"
        )

        self.log.see("end")

        self.log.configure(
            state="disabled"
        )

        self.root.update_idletasks()

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self):

        self.numbers_var.set("")

        self.log.configure(
            state="normal"
        )

        self.log.delete(
            "1.0",
            "end"
        )

        self.log.configure(
            state="disabled"
        )

    # ========================================================
    # PARSE NOMOR
    # ========================================================

    def parse_selections(self, text):
        """
        Parser fleksibel untuk hasil copy dari WhatsApp / Excel / chat.

        Contoh yang diterima:
            SAD06736.JPG
            1. SAD06736.JPG
            2) SAD06764.JPG
            - SAD06762.JPG
            • SAD06671.JPG
            SAD06736.JPG, SAD06764.JPG
            SAD06736.JPG    SAD06764.JPG
            Foto pilihan: SAD06736.JPG
            C:\\FOTO\\SAD06736.JPG
            /Users/user/FOTO/SAD06736.JPG
            SAD06736
            6736

        Prioritas parser:
        1. Cari token yang terlihat seperti nama file foto lengkap.
        2. Cari stem kamera yang mengandung huruf + angka.
        3. Kalau satu baris hanya berisi angka, angka tersebut dianggap
           nomor foto.
        """

        known_exts = sorted(
            RAW_EXTENSIONS | IMAGE_EXTENSIONS,
            key=len,
            reverse=True
        )

        ext_pattern = "|".join(
            re.escape(ext.lstrip("."))
            for ext in known_exts
        )

        selections = []
        seen = set()

        def add_item(original, stem=None, number=None):
            original = original.strip().strip('"').strip("'")

            if not original:
                return

            if stem is not None:
                stem_key = stem.casefold()
                key = ("stem", stem_key)
            else:
                stem_key = None
                key = ("number", number)

            if key in seen:
                return

            seen.add(key)

            selections.append({
                "original": original,
                "stem": stem_key,
                "number": number,
            })

        # =====================================================
        # 1. CARI NAMA FILE LENGKAP DENGAN EKSTENSI
        # =====================================================

        file_pattern = re.compile(
            rf'''(?ix)
            (?:
                [A-Z]:[\\/][^\r\n,;]+?[\\/]
                |
                /[^\r\n,;]+?/
            )?
            ([A-Z0-9][A-Z0-9_().\-]*?\.(?:{ext_pattern}))
            (?=$|[\s,;)\]}}>"'])
            '''
        )

        matched_spans = []

        for match in file_pattern.finditer(text):
            filename = match.group(1).strip()
            filename = Path(filename).name

            # Bersihkan nomor urut/bullet yang ikut menempel dari WhatsApp/Excel.
            # Contoh:
            # "1. SAD06736.JPG"  -> "SAD06736.JPG"
            # "2) SAD06764.JPG"  -> "SAD06764.JPG"
            filename = re.sub(
                r"^\s*\d+\s*[.):\-]\s*",
                "",
                filename
            )
            filename = re.sub(
                r"^[\-\u2022\u2023\u25E6\u2043\u2219*]+\s*",
                "",
                filename
            )

            stem = Path(filename).stem.strip()
            number = extract_number(filename)

            add_item(
                original=filename,
                stem=stem,
                number=number
            )

            matched_spans.append(match.span())

        remaining_chars = list(text)

        for a, b in matched_spans:
            for i in range(a, b):
                remaining_chars[i] = " "

        remaining = "".join(remaining_chars)

        # =====================================================
        # 2. CARI STEM TANPA EKSTENSI
        # =====================================================

        stem_pattern = re.compile(
            r'''(?ix)
            (?<![A-Z0-9])
            (
                (?=[A-Z0-9_.\-]*[A-Z])
                (?=[A-Z0-9_.\-]*\d)
                [A-Z][A-Z0-9_.\-]*\d[A-Z0-9_.\-]*
            )
            (?![A-Z0-9])
            '''
        )

        stem_spans = []

        for match in stem_pattern.finditer(remaining):
            token = match.group(1).strip(" .,-_;")

            if not token:
                continue

            if len(token) < 3:
                continue

            number = extract_number(token)

            add_item(
                original=token,
                stem=token,
                number=number
            )

            stem_spans.append(match.span())

        remaining_chars = list(remaining)

        for a, b in stem_spans:
            for i in range(a, b):
                remaining_chars[i] = " "

        remaining = "".join(remaining_chars)

        # =====================================================
        # 3. INPUT ANGKA MURNI
        # =====================================================

        for raw_line in remaining.splitlines():

            line = raw_line.strip()

            if not line:
                continue

            line = re.sub(
                r"^[\-\u2022\u2023\u25E6\u2043\u2219*]+\s*",
                "",
                line
            )

            if re.fullmatch(r"\d+", line):

                value = int(line)

                if value > 0:
                    add_item(
                        original=line,
                        stem=None,
                        number=value
                    )

                continue

            if re.fullmatch(r"[\d\s,;\t]+", line):

                for n in re.findall(r"\d+", line):

                    value = int(n)

                    if value > 0:
                        add_item(
                            original=n,
                            stem=None,
                            number=value
                        )

        return selections


    # ========================================================
    # BUILD INDEX
    # ========================================================

    def build_index(self, source, output=None):
        """
        Scan REKURSIF seluruh folder di bawah folder sumber.

        Contoh:
            Wedding Anjas/
                Canon/
                Sony/
                Kamera 3/
                Backup/JPG/

        Semua folder di atas akan ikut dicari otomatis.

        Folder output/SELECTED akan dilewati supaya file hasil
        yang sudah dipindahkan tidak ikut terbaca lagi.
        """

        raw_by_stem = {}
        jpg_by_stem = {}

        raw_by_number = {}
        jpg_by_number = {}

        source_resolved = source.resolve()

        output_resolved = None

        if output is not None:
            try:
                output_resolved = output.resolve()
            except Exception:
                output_resolved = None

        # rglob("*") = mencari sampai ke semua subfolder bertingkat
        for p in source.rglob("*"):

            if not p.is_file():
                continue

            # Jangan scan file di dalam folder output.
            if output_resolved is not None:

                try:
                    p_resolved = p.resolve()

                    # Python 3.9+ support is_relative_to
                    if p_resolved.is_relative_to(output_resolved):
                        continue

                except Exception:
                    # Fallback aman kalau resolve/is_relative_to gagal
                    try:
                        p.relative_to(output)
                        continue
                    except Exception:
                        pass

            ext = p.suffix.lower()
            stem_key = p.stem.casefold()
            number = extract_number(p.name)

            if ext in RAW_EXTENSIONS:

                raw_by_stem.setdefault(
                    stem_key,
                    []
                ).append(p)

                if number is not None:
                    raw_by_number.setdefault(
                        number,
                        []
                    ).append(p)

            elif ext in IMAGE_EXTENSIONS:

                jpg_by_stem.setdefault(
                    stem_key,
                    []
                ).append(p)

                if number is not None:
                    jpg_by_number.setdefault(
                        number,
                        []
                    ).append(p)

        return (
            raw_by_stem,
            jpg_by_stem,
            raw_by_number,
            jpg_by_number
        )


    # ========================================================
    # PROCESS
    # ========================================================

    def process(self):

        source = Path(
            self.source_var.get().strip()
        )

        output = Path(
            self.output_var.get().strip()
        )

        # ----------------------------------------------------
        # CEK SOURCE
        # ----------------------------------------------------

        if not source.is_dir():

            messagebox.showerror(
                "Folder sumber belum dipilih",
                "Pilih folder induk RAW/JPG yang benar."
            )

            return

        # ----------------------------------------------------
        # PARSE NOMOR
        # ----------------------------------------------------

        selections = self.parse_selections(
            self.numbers_var.get()
        )

        if not selections:

            messagebox.showerror(
                "Pilihan belum diisi",
                "Paste nama file / nomor pilihan client dari WhatsApp, Excel, atau daftar biasa."
            )

            return

        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        try:

            output.mkdir(
                parents=True,
                exist_ok=True
            )

        except Exception as exc:

            messagebox.showerror(
                "Folder tujuan gagal dibuat",
                str(exc)
            )

            return

        # ----------------------------------------------------
        # LOG HEADER
        # ----------------------------------------------------

        self.write_log("")

        self.write_log(
            "=" * 72
        )

        self.write_log(
            "MODE: MOVE / CUT"
        )

        self.write_log(
            f"APP    : {APP_TITLE} v{APP_VERSION}"
        )

        self.write_log(
            f"SUMBER : {source}"
        )

        self.write_log(
            "SCAN   : Semua subfolder (rekursif)"
        )

        self.write_log(
            f"TUJUAN : {output}"
        )

        self.write_log(
            "PILIHAN: " +
            ", ".join(item["original"] for item in selections)
        )

        self.write_log(
            "=" * 72
        )

        # ----------------------------------------------------
        # BUILD INDEX
        # ----------------------------------------------------

        (
            raw_by_stem,
            jpg_by_stem,
            raw_by_number,
            jpg_by_number
        ) = self.build_index(
            source,
            output
        )

        moved = 0
        missing = []
        skipped = 0

        # ----------------------------------------------------
        # PROCESS EACH NUMBER
        # ----------------------------------------------------

        for item in selections:

            original = item["original"]
            stem_key = item["stem"]
            number = item["number"]

            matches = []
            source_type = "RAW"
            matched_by = ""

            # =================================================
            # 1. PRIORITAS: NAMA DASAR FILE PERSIS
            # =================================================
            if stem_key is not None:

                matches = raw_by_stem.get(
                    stem_key,
                    []
                )

                if matches:
                    matched_by = "nama file"

                # =============================================
                # FALLBACK JPG DENGAN NAMA DASAR YANG SAMA
                # =============================================
                if not matches:

                    matches = jpg_by_stem.get(
                        stem_key,
                        []
                    )

                    if matches:
                        source_type = "JPG/JPEG"
                        matched_by = "nama file"

            # =================================================
            # 2. INPUT ANGKA SAJA → CARI BERDASARKAN NOMOR
            # =================================================
            else:

                matches = raw_by_number.get(
                    number,
                    []
                )

                if matches:
                    matched_by = "nomor"

                if not matches:

                    matches = jpg_by_number.get(
                        number,
                        []
                    )

                    if matches:
                        source_type = "JPG/JPEG"
                        matched_by = "nomor"

            # =================================================
            # TIDAK DITEMUKAN
            # =================================================
            if not matches:

                missing.append(original)

                self.write_log(
                    f"✗ {original}: RAW dan JPG/JPEG tidak ditemukan"
                )

                continue

            # =================================================
            # INFO FALLBACK
            # =================================================
            if source_type == "JPG/JPEG":

                self.write_log(
                    f"⚠ {original}: RAW tidak ada → fallback ke JPG/JPEG"
                )

            # =================================================
            # MOVE
            # =================================================
            for src in matches:

                dst = output / src.name

                if dst.exists():

                    skipped += 1

                    self.write_log(
                        f"⚠ {original}: "
                        f"{src.name} sudah ada di tujuan → dilewati"
                    )

                    continue

                try:

                    shutil.move(
                        str(src),
                        str(dst)
                    )

                    if self.readonly_var.get():

                        current_mode = os.stat(
                            dst
                        ).st_mode

                        os.chmod(
                            dst,
                            current_mode & ~0o222
                        )

                    moved += 1

                    try:
                        lokasi_asal = src.parent.relative_to(source)
                    except Exception:
                        lokasi_asal = src.parent

                    self.write_log(
                        f"✓ {original}: "
                        f"{src.name} → DIPINDAHKAN "
                        f"({source_type}, cocok via {matched_by}, "
                        f"dari: {lokasi_asal})"
                    )

                except Exception as exc:

                    self.write_log(
                        f"✗ {original}: "
                        f"{src.name} → GAGAL: {exc}"
                    )

        # ----------------------------------------------------
        # FINISH
        # ----------------------------------------------------

        self.write_log(
            "-" * 72
        )

        self.write_log(
            f"SELESAI — "
            f"{moved} file berhasil dipindahkan."
        )

        if skipped:

            self.write_log(
                f"{skipped} file dilewati "
                "karena sudah ada di folder tujuan."
            )

        if missing:

            self.write_log(
                "Tidak ditemukan: " +
                ", ".join(missing)
            )

        # ----------------------------------------------------
        # MESSAGE
        # ----------------------------------------------------

        message = (
            "Selesai!\n\n"
            f"{moved} file berhasil DIPINDAHKAN ke:\n"
            f"{output}"
        )

        if skipped:

            message += (
                f"\n\n{skipped} file dilewati "
                "karena sudah ada di tujuan."
            )

        if missing:

            message += (
                "\n\nRAW/JPG tidak ditemukan "
                "untuk pilihan: " +
                ", ".join(missing)
            )

        messagebox.showinfo(
            "Proses selesai",
            message
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    App(root)

    root.mainloop()