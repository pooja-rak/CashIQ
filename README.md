# 💳 CashIQ – Smart ATM Locator & Analyzer

## 📌 Overview

**CashIQ** is a smart location-based application that helps users find nearby ATMs and provides real-time insights such as ATM condition, cash availability, and crowd level.

The goal of this project is to reduce user inconvenience by helping them choose the most suitable ATM 

---

## 🚀 Features

* 📍 **Nearby ATM Detection** based on user location
* 💰 **Cash Availability Status** (Available / Low / Out of Cash)
* 🧍 **Crowd Level Analysis** (Low / Medium / High)
* 🏧 **ATM Condition Status** (Working / Maintenance / Out of Service)
* 🗺️ **Navigation Support** to selected ATM
* ⚡ **User-friendly Interface** for quick decision-making

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit**
* **Openstreet Maps API**
* **Geolocation Services**
* **Pandas / NumPy**

---

## 📂 Project Structure

```
cashiq/
│── app.py
│── utils.py
│── config.py
│── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/pooja-rak/cashiq.git
cd cashiq
```

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 3️⃣ Run the application

```
streamlit run app.py
```

---

## 🧠 How It Works

1. User location is captured
2. Nearby ATMs are fetched using map APIs
3. Each ATM is analyzed based on:

   * Cash availability
   * Crowd level
   * Operational condition
4. User selects preferred ATM
5. App provides navigation to the selected ATM

---

## 🔐 Disclaimer ⚠️

> This project is developed for **educational and demonstration purposes**.

* The application relies on **external APIs (such as External API)**
* Secure API keys and authentication mechanisms are required
* Public deployment may expose sensitive credentials and lead to misuse or billing issues

👉 Therefore:

* This project is intended for **local execution and demonstration only**
* Full deployment is restricted due to **API security and authentication limitations**

---

## 💡 Future Enhancements

* Real-time ATM data integration (bank APIs)
* Secure API key management using environment variables
* User login & personalization
* Advanced UI/UX improvements
* Offline support for navigation

---

## 🎯 Project Objective

To build an intelligent system that helps users:

* Save time finding ATMs
* Avoid crowded or non-functional machines
* Improve overall banking convenience

---

## 🤝 Contribution

Contributions are welcome! Feel free to fork and enhance the project.

---

## 📜 License

This project is for educational purposes.

---

## 👩‍💻 Author

**Pooja**
Aspiring Machine Learning Engineer 🚀
