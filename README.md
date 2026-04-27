# Progress 3: Simple LMS - REST API dengan Django Ninja

> Sebuah sistem Learning Management System (LMS) yang sederhana namun lengkap, dibangun dengan Django Ninja, JWT authentication, dan role-based authorization. Cocok sebagai pembelajaran atau starting point untuk project yang lebih besar.
---

## 🚀 Cara Menjalankan Project

### ⚡ Cara Paling Mudah: Docker Compose

**Jika Anda punya Docker installed:**

```bash
cd d:\PSS\lms-progress3
docker-compose up -d
```

Tunggu beberapa detik, kemudian buka browser:

- 🌐 **Lihat dokumentasi API**: http://localhost:8000/api/docs
- 📊 **Format berbeda**: http://localhost:8000/api/redoc
- 🎯 **Base URL API**: http://localhost:8000/api/

**Itu aja!** Semua sudah jalan.

### 🛠️ Cara Manual (Tanpa Docker)

Jika Anda prefer development langsung di local:

```bash
# 1. Masuk ke folder
cd d:\PSS\lms-progress3\code

# 2. Buat virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python manage.py migrate

# 5. Jalankan server
python manage.py runserver
```

Kemudian buka: http://localhost:8000/api/docs

---

## 📚 15 Endpoint API - Apa Aja Sih?

### 🔐 **Authentication (5 endpoint)**

Ini tentang login/registrasi:

- `POST /api/auth/register` - Daftar user baru
- `POST /api/auth/login` - Login, dapat token
- `POST /api/auth/refresh` - Perpanjang token
- `GET /api/auth/me` - Lihat profil saya
- `PUT /api/auth/me` - Edit profil saya

### 📚 **Courses (5 endpoint)**

Ini tentang kursus/pelajaran:

- `GET /api/courses` - Lihat daftar kursus (semua orang bisa)
- `GET /api/courses/{id}` - Lihat detail 1 kursus
- `POST /api/courses` - Buat kursus baru (hanya instructor)
- `PATCH /api/courses/{id}` - Edit kursus (hanya pemilik/admin)
- `DELETE /api/courses/{id}` - Hapus kursus (hanya admin)

### 📝 **Enrollments (5 endpoint)**

Ini tentang pendaftaran siswa:

- `POST /api/enrollments` - Daftar ke sebuah kursus
- `GET /api/enrollments/my-courses` - Lihat kursus saya
- `POST /api/enrollments/{id}/progress` - Tandai sudah selesai

**Bonus:** Ada juga pagination dan filtering untuk list kursus (cari by level, price, dsb)

---

## 🎯 Fitur-Fitur Penting

### 1️⃣ **Login/Logout yang Aman**

Menggunakan JWT token. Jadi:

- Anda login → dapat token
- Token itu kayak kartu masuk yang valid 1 jam
- Setelah expired, bisa di-refresh
- Tidak perlu session di server (stateless)

### 2️⃣ **3 Tipe User Berbeda**

Beda hak akses:

- **Student** - Hanya bisa daftar kursus dan lihat progress
- **Instructor** - Bisa buat dan edit kursus miliknya
- **Admin** - Full access, bisa hapus kursus siapa aja

### 3️⃣ **Validasi Input yang Ketat**

Pakai Pydantic, jadi:

- Email harus format email yang benar
- Password minimal 6 karakter
- Tidak ada spam atau data jelek yang masuk

### 4️⃣ **Dokumentasi Otomatis**

Buka `/api/docs`, langsung bisa:

- Lihat semua endpoint
- Lihat format request/response
- **Test endpoint langsung** dari browser (klik "Try it out")

### 5️⃣ **Praktis di-Test**

- File `LMS_API.postman_collection.json` disediakan
- Import ke Postman, langsung bisa test semua endpoint
- Ada script otomatis untuk capture token

---

## 🧪 Cara Testing API

### **Option 1: Swagger UI (PALING MUDAH)**

1. Buka http://localhost:8000/api/docs
2. Klik tombol **Authorize** (kunci icon)
3. Paste token di sini
4. Klik "Try it out" di endpoint apapun

### **Option 2: Postman Collection**

1. Buka Postman
2. **File** → **Import** → pilih `LMS_API.postman_collection.json`
3. Run requests, token otomatis ter-capture

### **Option 3: cURL (untuk yang adventurous)**

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@mail.com","password":"pass123"}'

# Lihat profil (butuh token)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🏗️ Teknologi yang Dipakai

| Apa              | Fungsi                                         |
| ---------------- | ---------------------------------------------- |
| **Django 5.1**   | Framework Python untuk backend                 |
| **Django Ninja** | Library buat bikin REST API yang lebih simpel  |
| **PostgreSQL**   | Database untuk simpan data                     |
| **JWT**          | System login yang aman                         |
| **Pydantic**     | Validasi input data                            |
| **Docker**       | Containerize app biar mudah di-run di mana aja |

---

## 📁 Struktur Folder (Jangan Pusing)

```
project/
├── docker-compose.yml       ← Setup Docker
├── requirements.txt         ← Python packages
├── LMS_API.postman_collection.json  ← Test collection
│
└── code/
    ├── manage.py            ← Perintah Django
    ├── lms/
    │   └── api.py          ← Main router (semua endpoint di sini)
    │
    ├── accounts/           ← Authentication (login/register)
    ├── courses/            ← Manajemen kursus
    └── enrollments/        ← Manajemen pendaftaran siswa
```

---

## 🔒 Keamanan

Sudah diperhatikan:

- ✅ Password di-hash, bukan disimpen plain text
- ✅ JWT token punya expiration time
- ✅ Setiap endpoint di-protect sesuai role user
- ✅ Input validation ketat (tidak bisa injection)

---

## ❓ Gimana Cara Testing?

**Scenario 1: Test Register**

1. Buka http://localhost:8000/api/docs
2. Find endpoint "POST /api/auth/register"
3. Klik "Try it out"
4. Isi form:
   - username: "john"
   - email: "john@mail.com"
   - password: "pass123"
   - role: "student"
5. Klik "Execute"
6. Lihat response, harusnya 201 dan dapat token

**Scenario 2: Test Create Course (Instructor)**

1. Register sebagai instructor (role: "instructor")
2. Copy access_token dari response
3. Klik "Authorize", paste token
4. Find endpoint "POST /api/courses"
5. Isi form, klik Execute
6. Harusnya berhasil create course

**Scenario 3: Test Delete Course (Student dapat 403)**

1. Login sebagai student
2. Try DELETE /api/courses/{id}
3. Response: 403 Forbidden
4. ✅ Benar! Student tidak boleh delete course

---

## 🆘 Troubleshooting (Kalau Ada Masalah)

**Q: Docker tidak jalan**
A: Install Docker Desktop dulu dari docker.com

**Q: Port 8000 sudah terpakai**
A: Edit docker-compose.yml, ubah `"8000:8000"` ke `"8001:8000"`

**Q: ERROR 500 saat login**
A: Cek docker logs: `docker-compose logs`

**Q: Semua endpoint return 401 Unauthorized**
A: Token sudah expired atau format header salah. Format yang benar:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

**Q: Postman collection gak bisa import**
A: Pastikan file `LMS_API.postman_collection.json` ada di folder root

---

**Next steps:**

1. Run: `docker-compose up -d`
2. Test: Buka http://localhost:8000/api/docs
3. Push ke GitHub
4. Submit ke KULINO

**Good luck! 🚀**
