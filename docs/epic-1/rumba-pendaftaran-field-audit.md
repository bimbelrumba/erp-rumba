# Audit Field RUMBA Pendaftaran

## Konteks

Audit ini menjadi langkah awal Epic 1 "Fondasi Data dan Workflow Inti". Fokusnya adalah menilai apakah field pada doctype `RUMBA Pendaftaran` sudah cukup rapi untuk mendukung alur:

1. calon murid mendaftar,
2. admin memverifikasi,
3. data diterima,
4. murid aktif dibentuk di `RUMBA Murid`.

Referensi utama:

- `bimbelrumba/bimbel_rumba/doctype/rumba_pendaftaran/rumba_pendaftaran.json`
- `bimbelrumba/bimbel_rumba/doctype/rumba_pendaftaran/rumba_pendaftaran.py`
- `bimbelrumba/bimbel_rumba/doctype/rumba_murid/rumba_murid.json`

## Ringkasan Kondisi Saat Ini

`RUMBA Pendaftaran` saat ini sudah memuat hampir seluruh data intake calon murid, tetapi masih mencampur tiga lapisan data dalam satu form:

- data formulir pendaftaran,
- data operasional/admin pasca verifikasi,
- data yang nantinya juga hidup di `RUMBA Murid`.

Secara struktur, doctype ini sudah cukup untuk pengumpulan data awal. Namun untuk fondasi workflow inti, masih ada beberapa celah:

- belum ada logika Python untuk transisi status atau pembuatan `RUMBA Murid`,
- field admin masih bercampur dengan field intake publik,
- ada banyak field kondisional yang belum dipaksa validasinya,
- ada duplikasi data dengan `RUMBA Murid` yang belum didefinisikan sebagai source of truth.

## Klasifikasi Field

### A. Field inti intake pendaftaran

Field ini penting untuk menangkap identitas, pilihan belajar, dan kontak utama.

| Kelompok | Field |
| --- | --- |
| Identitas anak | `nama_lengkap`, `nama_panggilan`, `tempat_lahir`, `tanggal_lahir`, `jenis_kelamin`, `agama_kepercayaan` |
| Sekolah dan alamat | `sudah_sekolah`, `nama_sekolah`, `kelas_sekolah`, `alamat_rumah` |
| Orang tua/wali | `nama_ortu`, `hubungan_ortu`, `pekerjaan_ortu`, `pendidikan_ortu`, `email_ortu`, `nomor_hape` |
| Pilihan belajar | `kota_rumba`, `cabang_rumba`, `kode_cabang`, `program_belajar`, `senin`-`sabtu`, `jam_belajar` |
| Tanggal referensi intake | `tanggal_pendaftaran` |

Status audit:

- sudah relevan untuk intake awal,
- beberapa field sudah `reqd`,
- `kode_cabang` sudah benar sebagai field turunan dari `cabang_rumba`.

### B. Field intake tambahan

Field ini berguna untuk profiling murid dan konteks layanan, tetapi bukan inti pembentukan entitas murid.

| Kelompok | Field |
| --- | --- |
| Saudara di RUMBA | `saudara_di_rumba`, `nama_saudara`, `belajar_di_rumba` |
| Media sosial ortu | `follow_akun_medsos`, `nama_akun_fb`, `nama_akun_ig`, `nama_akun_tiktok`, `nama_akun_medsos_lainnya` |
| Aktivitas anak | `kegiatan_anak_di_rumah`, `hal_menonjol`, `pengembangan_lanjutan`, `harapan_ortu` |
| Kebutuhan belajar | `kebutuhan_khusus`, `penjelasan_kebutuhan_khusus`, `les_serupa`, `durasi_les`, `level_yang_dicapai`, `nama_tempat_les` |
| Sumber informasi | `facebook`, `instagram`, `tiktok`, `website_bimbelrumbacom`, `pencarian_internet`, `spandukbanner`, `keluarga__kawan`, `kegiatan_rumba`, `sekolah`, `lainnya`, `penjelasan_lainnya` |
| Merchandise | `kaos`, `ukuran_kaos`, `topi`, `tas` |
| Persetujuan | `konfirmasi_data`, `kebijakan_no_refund` |

Status audit:

- masih layak disimpan di doctype pendaftaran,
- sebagian besar idealnya bersifat opsional,
- membutuhkan validasi kondisional supaya data tidak setengah terisi.

### C. Field operasional/admin

Field berikut bukan data intake murni, melainkan hasil proses backoffice.

| Field | Fungsi |
| --- | --- |
| `tanggal_mulai_belajar` | keputusan operasional setelah diterima |
| `nomor_induk_murid` | identitas resmi murid aktif |
| `rumba_murid` | relasi ke record murid aktif |
| `metode_pembayaran` | detail administrasi pembayaran |
| `status_bayar` | status pembayaran |
| `status_pendaftaran` | status workflow |

Status audit:

- benar secara domain,
- tetapi sebaiknya diposisikan jelas sebagai area admin-only dan bukan bagian intake awal.

## Temuan Utama

### 1. Source of truth belum tegas antara pendaftaran dan murid

`RUMBA Murid` mengambil sebagian data dari `RUMBA Pendaftaran`, misalnya:

- `nama_lengkap`
- `nama_panggilan`
- `email_ortu`
- `nomor_hape`
- referensi `pendaftaran_rujukan`

Tetapi banyak field penting lain di `RUMBA Murid` masih berdiri sendiri, seperti:

- `program_belajar`
- pilihan hari belajar (`senin`-`sabtu`)
- `jam_belajar`
- `tanggal_pendaftaran`
- `tanggal_mulai_belajar`
- `metode_pembayaran`
- `status_pembayaran`

Artinya, hubungan antar doctype sudah ada, tetapi belum konsisten. Risiko utamanya adalah data drift antara pendaftaran dan murid aktif.

### 2. Workflow status belum dijaga oleh logika server

`rumba_pendaftaran.py` masih kosong. Saat ini belum ada guardrail untuk memastikan:

- `status_pendaftaran = Diterima` hanya boleh saat data admin lengkap,
- `status_pendaftaran = Ditolak` punya alasan atau catatan,
- `rumba_murid` dibuat hanya sekali,
- `nomor_induk_murid` dibangkitkan saat accepted, bukan diisi manual sembarang.

Ini adalah gap paling penting untuk Epic 1.

### 3. Banyak field kondisional belum tervalidasi

Contoh hubungan yang seharusnya divalidasi:

- jika `sudah_sekolah = Sudah`, maka `nama_sekolah` dan `kelas_sekolah` wajib,
- jika `saudara_di_rumba = Ya`, maka `nama_saudara` minimal wajib,
- jika `kebutuhan_khusus = Ya`, maka `penjelasan_kebutuhan_khusus` wajib,
- jika `les_serupa = Ya`, maka `durasi_les` atau `nama_tempat_les` perlu diisi,
- jika `lainnya = 1`, maka `penjelasan_lainnya` wajib,
- jika `kaos = 1`, maka `ukuran_kaos` wajib.

Saat ini struktur field sudah mendukung, tetapi enforcement belum ada.

### 4. `hari_belajar` dan `sumber_informasi`/`merchandise_rumba` berupa `HTML`

Field:

- `hari_belajar`
- `sumber_informasi`
- `merchandise_rumba`

dipakai sebagai elemen presentasi, bukan data. Ini aman untuk UI, tetapi perlu dipastikan tidak dianggap sebagai field bisnis. Untuk audit domain, field-field ini sebaiknya diperlakukan sebagai dekoratif.

### 5. Pendaftaran masih terlalu "gemuk" untuk fondasi data inti

Untuk fase Epic 1, data minimum yang benar-benar dibutuhkan agar workflow inti berjalan adalah:

- identitas anak,
- kontak orang tua,
- cabang/program/jadwal,
- tanggal pendaftaran,
- status pendaftaran,
- tanggal mulai belajar,
- status/metode pembayaran,
- relasi ke `RUMBA Murid`.

Bagian profiling, medsos, merchandise, dan sumber informasi bisa tetap ada, tetapi jangan menghambat alur utama.

## Rekomendasi Prioritas

### Prioritas 1: tetapkan field minimum untuk workflow inti

Tandai sebagai field yang wajib lengkap sebelum status `Diterima`:

- `kota_rumba`
- `cabang_rumba`
- `program_belajar`
- minimal satu hari belajar
- `jam_belajar`
- `nama_lengkap`
- `nama_panggilan`
- `tanggal_lahir`
- `sudah_sekolah`
- `alamat_rumah`
- `nama_ortu`
- `email_ortu`
- `nomor_hape`
- `tanggal_mulai_belajar`
- `metode_pembayaran`
- `status_bayar`

### Prioritas 2: tegaskan field yang berasal dari pendaftaran ke murid

Untuk Epic 1, lebih aman bila `RUMBA Pendaftaran` menjadi source awal untuk:

- data identitas murid,
- data kontak orang tua,
- pilihan program dan jadwal,
- metadata awal administrasi.

Lalu `RUMBA Murid` menyimpan hasil final operasional dan referensi balik ke pendaftaran.

### Prioritas 3: tambah validasi server-side

Minimal validasi yang perlu ada:

- wajib minimal satu hari belajar,
- wajib isi pasangan field kondisional,
- cegah accept tanpa field admin kunci,
- cegah pembuatan `RUMBA Murid` ganda dari satu pendaftaran.

### Prioritas 4: pisahkan audit field menjadi 4 status implementasi

Usulan penandaan untuk pekerjaan berikutnya:

- `core-intake`
- `conditional-intake`
- `admin-workflow`
- `decorative-ui`

Penandaan ini akan mempermudah refactor doctype dan penulisan validasi.

## Usulan Langkah Berikutnya

Setelah audit ini, urutan paling masuk akal untuk Epic 1 adalah:

1. normalisasi field inti `RUMBA Pendaftaran`,
2. tambah validasi server-side pada `RUMBA Pendaftaran`,
3. definisikan aksi acceptance untuk membuat `RUMBA Murid`,
4. sinkronkan field duplikat antara `RUMBA Pendaftaran` dan `RUMBA Murid`,
5. baru lanjut ke workflow admin dan otomatisasi nomor induk murid.

## Keputusan Sementara

Untuk tahap audit ini, saya merekomendasikan keputusan kerja berikut:

- `RUMBA Pendaftaran` tetap dipertahankan sebagai intake master,
- `RUMBA Murid` diperlakukan sebagai entitas hasil penerimaan,
- field profiling tambahan tidak dihapus dulu,
- implementasi berikutnya fokus ke validasi dan transisi status, bukan redesign besar-besaran.
