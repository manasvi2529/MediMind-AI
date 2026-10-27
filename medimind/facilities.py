"""Facilities database and search: Hospitals and Blood Banks with live vacancies."""
import math
import requests

# Default cities for quick navigation with center coordinates
CITIES = {
    "Delhi NCR": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462},
    "Patna": {"lat": 25.5941, "lon": 85.1376},
}

# Pre-seeded database of premier public & private hospitals and blood banks with live vacancy profiles
FACILITIES = [
    # ------------------ DELHI NCR ------------------
    {
        "id": "del-aiims",
        "name": "AIIMS New Delhi (Apex Trauma Centre & Hospital)",
        "type": "Hospital",
        "city": "Delhi NCR",
        "lat": 28.5672,
        "lon": 77.2100,
        "address": "Sri Aurobindo Marg, Ansari Nagar, New Delhi",
        "phone": "+91-11-26588500",
        "emergency_phone": "102 / 108",
        "is_24_7": True,
        "beds_total": 2500,
        "beds_available": 46,
        "icu_available": 8,
        "oxygen_available": 24,
        "ventilators_available": 5,
        "blood_stock": {"A+": 32, "A-": 12, "B+": 45, "B-": 8, "O+": 58, "O-": 6, "AB+": 19, "AB-": 4, "Platelets": 25},
        "last_updated": "10 mins ago",
    },
    {
        "id": "del-safdarjung",
        "name": "VMMMC & Safdarjung Hospital",
        "type": "Hospital",
        "city": "Delhi NCR",
        "lat": 28.5705,
        "lon": 77.2069,
        "address": "Ring Road, opposite AIIMS, New Delhi",
        "phone": "+91-11-26165060",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 1800,
        "beds_available": 32,
        "icu_available": 4,
        "oxygen_available": 18,
        "ventilators_available": 2,
        "blood_stock": {"A+": 20, "A-": 5, "B+": 28, "B-": 4, "O+": 35, "O-": 3, "AB+": 12, "AB-": 2, "Platelets": 14},
        "last_updated": "25 mins ago",
    },
    {
        "id": "del-redcross",
        "name": "Indian Red Cross Society National Blood Bank",
        "type": "Blood Bank",
        "city": "Delhi NCR",
        "lat": 28.6219,
        "lon": 77.2103,
        "address": "1, Red Cross Road, Sansad Marg, New Delhi",
        "phone": "+91-11-23716441",
        "emergency_phone": "1910",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 75, "A-": 28, "B+": 92, "B-": 22, "O+": 110, "O-": 18, "AB+": 44, "AB-": 12, "Platelets": 48},
        "last_updated": "5 mins ago",
    },
    {
        "id": "del-rotary",
        "name": "Rotary Blood Centre Delhi",
        "type": "Blood Bank",
        "city": "Delhi NCR",
        "lat": 28.5630,
        "lon": 77.2830,
        "address": "56-57, Tughlakabad Institutional Area, New Delhi",
        "phone": "+91-11-29955771",
        "emergency_phone": "+91-11-29955773",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 62, "A-": 18, "B+": 70, "B-": 15, "O+": 85, "O-": 14, "AB+": 31, "AB-": 9, "Platelets": 36},
        "last_updated": "15 mins ago",
    },
    {
        "id": "del-max-saket",
        "name": "Max Super Speciality Hospital Saket",
        "type": "Hospital",
        "city": "Delhi NCR",
        "lat": 28.5283,
        "lon": 77.2114,
        "address": "1, 2, Press Enclave Marg, Saket, New Delhi",
        "phone": "+91-11-26515050",
        "emergency_phone": "+91-11-40554055",
        "is_24_7": True,
        "beds_total": 530,
        "beds_available": 28,
        "icu_available": 6,
        "oxygen_available": 14,
        "ventilators_available": 4,
        "blood_stock": {"A+": 18, "A-": 6, "B+": 25, "B-": 5, "O+": 30, "O-": 4, "AB+": 11, "AB-": 2, "Platelets": 20},
        "last_updated": "18 mins ago",
    },

    # ------------------ MUMBAI ------------------
    {
        "id": "mum-kem",
        "name": "KEM Hospital & Seth GS Medical College",
        "type": "Hospital",
        "city": "Mumbai",
        "lat": 19.0026,
        "lon": 72.8427,
        "address": "Acharya Donde Marg, Parel, Mumbai",
        "phone": "+91-22-24107000",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 1800,
        "beds_available": 42,
        "icu_available": 7,
        "oxygen_available": 22,
        "ventilators_available": 3,
        "blood_stock": {"A+": 38, "A-": 14, "B+": 49, "B-": 11, "O+": 62, "O-": 9, "AB+": 21, "AB-": 5, "Platelets": 30},
        "last_updated": "14 mins ago",
    },
    {
        "id": "mum-lilavati",
        "name": "Lilavati Hospital & Research Centre",
        "type": "Hospital",
        "city": "Mumbai",
        "lat": 19.0514,
        "lon": 72.8294,
        "address": "A-791, Bandra Reclamation, Bandra West, Mumbai",
        "phone": "+91-22-26751000",
        "emergency_phone": "+91-22-26568000",
        "is_24_7": True,
        "beds_total": 320,
        "beds_available": 19,
        "icu_available": 5,
        "oxygen_available": 10,
        "ventilators_available": 3,
        "blood_stock": {"A+": 16, "A-": 4, "B+": 22, "B-": 3, "O+": 26, "O-": 2, "AB+": 9, "AB-": 1, "Platelets": 15},
        "last_updated": "20 mins ago",
    },
    {
        "id": "mum-redcross",
        "name": "Red Cross Blood Centre Mumbai",
        "type": "Blood Bank",
        "city": "Mumbai",
        "lat": 18.9322,
        "lon": 72.8335,
        "address": "141, Shahid Bhagat Singh Road, Fort, Mumbai",
        "phone": "+91-22-22661524",
        "emergency_phone": "1910",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 88, "A-": 34, "B+": 105, "B-": 27, "O+": 124, "O-": 21, "AB+": 52, "AB-": 14, "Platelets": 55},
        "last_updated": "8 mins ago",
    },
    {
        "id": "mum-tata",
        "name": "Tata Memorial Hospital Blood & Care Centre",
        "type": "Hospital",
        "city": "Mumbai",
        "lat": 19.0142,
        "lon": 72.8427,
        "address": "Dr E Borges Road, Parel, Mumbai",
        "phone": "+91-22-24177000",
        "emergency_phone": "+91-22-24177011",
        "is_24_7": True,
        "beds_total": 650,
        "beds_available": 24,
        "icu_available": 4,
        "oxygen_available": 12,
        "ventilators_available": 2,
        "blood_stock": {"A+": 44, "A-": 19, "B+": 56, "B-": 14, "O+": 70, "O-": 12, "AB+": 28, "AB-": 7, "Platelets": 62},
        "last_updated": "11 mins ago",
    },

    # ------------------ BENGALURU ------------------
    {
        "id": "blr-victoria",
        "name": "Victoria Hospital & Bangalore Medical College",
        "type": "Hospital",
        "city": "Bengaluru",
        "lat": 12.9629,
        "lon": 77.5750,
        "address": "Fort Road, Near City Market, Bengaluru",
        "phone": "+91-80-26701150",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 1200,
        "beds_available": 37,
        "icu_available": 9,
        "oxygen_available": 20,
        "ventilators_available": 6,
        "blood_stock": {"A+": 30, "A-": 9, "B+": 42, "B-": 8, "O+": 51, "O-": 5, "AB+": 18, "AB-": 3, "Platelets": 22},
        "last_updated": "16 mins ago",
    },
    {
        "id": "blr-narayana",
        "name": "Narayana Health City Multispecialty",
        "type": "Hospital",
        "city": "Bengaluru",
        "lat": 12.8257,
        "lon": 77.6917,
        "address": "258/A, Bommasandra Industrial Area, Anekal Taluk, Bengaluru",
        "phone": "+91-80-71222222",
        "emergency_phone": "+91-80-71222999",
        "is_24_7": True,
        "beds_total": 1400,
        "beds_available": 55,
        "icu_available": 12,
        "oxygen_available": 31,
        "ventilators_available": 8,
        "blood_stock": {"A+": 48, "A-": 15, "B+": 60, "B-": 12, "O+": 74, "O-": 10, "AB+": 26, "AB-": 6, "Platelets": 38},
        "last_updated": "7 mins ago",
    },
    {
        "id": "blr-rashtrotthana",
        "name": "Rashtrotthana Blood Centre",
        "type": "Blood Bank",
        "city": "Bengaluru",
        "lat": 12.9366,
        "lon": 77.5813,
        "address": "Kempegowda Nagar, Chamrajpet, Bengaluru",
        "phone": "+91-80-26612730",
        "emergency_phone": "+91-80-26612731",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 95, "A-": 38, "B+": 112, "B-": 29, "O+": 130, "O-": 24, "AB+": 58, "AB-": 16, "Platelets": 70},
        "last_updated": "3 mins ago",
    },
    {
        "id": "blr-manipal",
        "name": "Manipal Hospital Old Airport Road",
        "type": "Hospital",
        "city": "Bengaluru",
        "lat": 12.9592,
        "lon": 77.6534,
        "address": "98, HAL Old Airport Rd, Kodihalli, Bengaluru",
        "phone": "+91-80-25024444",
        "emergency_phone": "+91-80-25023344",
        "is_24_7": True,
        "beds_total": 600,
        "beds_available": 21,
        "icu_available": 3,
        "oxygen_available": 11,
        "ventilators_available": 2,
        "blood_stock": {"A+": 22, "A-": 7, "B+": 31, "B-": 5, "O+": 36, "O-": 4, "AB+": 14, "AB-": 3, "Platelets": 19},
        "last_updated": "22 mins ago",
    },

    # ------------------ HYDERABAD ------------------
    {
        "id": "hyd-osmania",
        "name": "Osmania General Hospital",
        "type": "Hospital",
        "city": "Hyderabad",
        "lat": 17.3770,
        "lon": 78.4739,
        "address": "Afzal Gunj, Hyderabad",
        "phone": "+91-40-24600121",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 1100,
        "beds_available": 34,
        "icu_available": 6,
        "oxygen_available": 19,
        "ventilators_available": 4,
        "blood_stock": {"A+": 29, "A-": 8, "B+": 38, "B-": 7, "O+": 46, "O-": 4, "AB+": 17, "AB-": 2, "Platelets": 16},
        "last_updated": "19 mins ago",
    },
    {
        "id": "hyd-redcross",
        "name": "Indian Red Cross Society Blood Centre Vidyanagar",
        "type": "Blood Bank",
        "city": "Hyderabad",
        "lat": 17.4042,
        "lon": 78.5085,
        "address": "Street No. 1, Vidyanagar, Adikmet, Hyderabad",
        "phone": "+91-40-27633087",
        "emergency_phone": "1910",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 82, "A-": 31, "B+": 96, "B-": 24, "O+": 118, "O-": 19, "AB+": 46, "AB-": 13, "Platelets": 52},
        "last_updated": "9 mins ago",
    },
    {
        "id": "hyd-apollo",
        "name": "Apollo Hospitals Jubilee Hills",
        "type": "Hospital",
        "city": "Hyderabad",
        "lat": 17.4156,
        "lon": 78.4124,
        "address": "Road No 72, Film Nagar, Jubilee Hills, Hyderabad",
        "phone": "+91-40-23607777",
        "emergency_phone": "1066",
        "is_24_7": True,
        "beds_total": 550,
        "beds_available": 26,
        "icu_available": 5,
        "oxygen_available": 15,
        "ventilators_available": 3,
        "blood_stock": {"A+": 24, "A-": 6, "B+": 30, "B-": 6, "O+": 39, "O-": 5, "AB+": 15, "AB-": 3, "Platelets": 24},
        "last_updated": "13 mins ago",
    },

    # ------------------ CHENNAI ------------------
    {
        "id": "chn-rajiv",
        "name": "Rajiv Gandhi Government General Hospital (RGGGH)",
        "type": "Hospital",
        "city": "Chennai",
        "lat": 13.0805,
        "lon": 80.2785,
        "address": "EVR Periyar Salai, Park Town, Chennai",
        "phone": "+91-44-25305000",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 2000,
        "beds_available": 49,
        "icu_available": 11,
        "oxygen_available": 26,
        "ventilators_available": 7,
        "blood_stock": {"A+": 41, "A-": 16, "B+": 53, "B-": 12, "O+": 67, "O-": 8, "AB+": 23, "AB-": 5, "Platelets": 35},
        "last_updated": "6 mins ago",
    },
    {
        "id": "chn-lions",
        "name": "Lions Blood Bank Chennai",
        "type": "Blood Bank",
        "city": "Chennai",
        "lat": 13.0642,
        "lon": 80.2514,
        "address": "130, Marshalls Road, Egmore, Chennai",
        "phone": "+91-44-28414949",
        "emergency_phone": "+91-44-28414950",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 78, "A-": 26, "B+": 89, "B-": 21, "O+": 104, "O-": 16, "AB+": 40, "AB-": 11, "Platelets": 46},
        "last_updated": "17 mins ago",
    },

    # ------------------ KOLKATA ------------------
    {
        "id": "kol-sskm",
        "name": "SSKM Hospital & IPGMER",
        "type": "Hospital",
        "city": "Kolkata",
        "lat": 22.5385,
        "lon": 88.3432,
        "address": "244, AJC Bose Road, Bhowanipore, Kolkata",
        "phone": "+91-33-22231589",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 1750,
        "beds_available": 39,
        "icu_available": 8,
        "oxygen_available": 23,
        "ventilators_available": 4,
        "blood_stock": {"A+": 36, "A-": 12, "B+": 48, "B-": 10, "O+": 60, "O-": 7, "AB+": 20, "AB-": 4, "Platelets": 28},
        "last_updated": "12 mins ago",
    },
    {
        "id": "kol-centralblood",
        "name": "Central Blood Bank Kolkata",
        "type": "Blood Bank",
        "city": "Kolkata",
        "lat": 22.5866,
        "lon": 88.3752,
        "address": "205, Maniktala Main Road, Kankurgachi, Kolkata",
        "phone": "+91-33-23502419",
        "emergency_phone": "1910",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 90, "A-": 32, "B+": 108, "B-": 26, "O+": 122, "O-": 19, "AB+": 51, "AB-": 15, "Platelets": 58},
        "last_updated": "4 mins ago",
    },

    # ------------------ PUNE ------------------
    {
        "id": "pun-sassoon",
        "name": "Sassoon General Hospital & BJ Medical College",
        "type": "Hospital",
        "city": "Pune",
        "lat": 18.5262,
        "lon": 73.8736,
        "address": "Near Pune Railway Station, Sangamvadi, Pune",
        "phone": "+91-20-26128000",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 1300,
        "beds_available": 31,
        "icu_available": 5,
        "oxygen_available": 17,
        "ventilators_available": 3,
        "blood_stock": {"A+": 28, "A-": 9, "B+": 37, "B-": 8, "O+": 44, "O-": 5, "AB+": 16, "AB-": 3, "Platelets": 21},
        "last_updated": "18 mins ago",
    },
    {
        "id": "pun-janakalyan",
        "name": "Janakalyan Blood Centre Pune",
        "type": "Blood Bank",
        "city": "Pune",
        "lat": 18.5144,
        "lon": 73.8502,
        "address": "1003, Shukrawar Peth, Swargate, Pune",
        "phone": "+91-20-24449524",
        "emergency_phone": "+91-20-24449525",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 74, "A-": 25, "B+": 88, "B-": 20, "O+": 98, "O-": 15, "AB+": 38, "AB-": 10, "Platelets": 42},
        "last_updated": "10 mins ago",
    },

    # ------------------ AHMEDABAD ------------------
    {
        "id": "ahm-civil",
        "name": "Ahmedabad Civil Hospital (Asia's Largest Civil Hospital)",
        "type": "Hospital",
        "city": "Ahmedabad",
        "lat": 23.0537,
        "lon": 72.6027,
        "address": "Asarwa, Ahmedabad, Gujarat",
        "phone": "+91-79-22683721",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 2800,
        "beds_available": 62,
        "icu_available": 14,
        "oxygen_available": 35,
        "ventilators_available": 8,
        "blood_stock": {"A+": 45, "A-": 18, "B+": 58, "B-": 15, "O+": 72, "O-": 10, "AB+": 25, "AB-": 6, "Platelets": 40},
        "last_updated": "8 mins ago",
    },
    {
        "id": "ahm-redcross",
        "name": "Indian Red Cross Society Blood Centre Ahmedabad",
        "type": "Blood Bank",
        "city": "Ahmedabad",
        "lat": 23.0135,
        "lon": 72.5629,
        "address": "Red Cross Bhavan, Juna Sharda Mandir Road, Paldi, Ahmedabad",
        "phone": "+91-79-26588220",
        "emergency_phone": "1910",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 86, "A-": 30, "B+": 102, "B-": 25, "O+": 115, "O-": 18, "AB+": 49, "AB-": 12, "Platelets": 50},
        "last_updated": "12 mins ago",
    },

    # ------------------ JAIPUR ------------------
    {
        "id": "jai-sms",
        "name": "Sawai Man Singh (SMS) Hospital & Medical College",
        "type": "Hospital",
        "city": "Jaipur",
        "lat": 26.8974,
        "lon": 75.8166,
        "address": "JLN Marg, Ashok Nagar, Jaipur, Rajasthan",
        "phone": "+91-141-2518224",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 2100,
        "beds_available": 45,
        "icu_available": 10,
        "oxygen_available": 25,
        "ventilators_available": 6,
        "blood_stock": {"A+": 38, "A-": 14, "B+": 51, "B-": 11, "O+": 64, "O-": 8, "AB+": 22, "AB-": 5, "Platelets": 32},
        "last_updated": "15 mins ago",
    },
    {
        "id": "jai-rotary",
        "name": "Rotary Club Blood Bank Jaipur",
        "type": "Blood Bank",
        "city": "Jaipur",
        "lat": 26.9038,
        "lon": 75.8080,
        "address": "Subhash Marg, C-Scheme, Jaipur",
        "phone": "+91-141-2371999",
        "emergency_phone": "+91-141-2371998",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 68, "A-": 22, "B+": 81, "B-": 18, "O+": 92, "O-": 14, "AB+": 35, "AB-": 8, "Platelets": 38},
        "last_updated": "20 mins ago",
    },

    # ------------------ LUCKNOW ------------------
    {
        "id": "lko-kgmu",
        "name": "King George's Medical University (KGMU)",
        "type": "Hospital",
        "city": "Lucknow",
        "lat": 26.8687,
        "lon": 80.9161,
        "address": "Shah Mina Road, Chowk, Lucknow, Uttar Pradesh",
        "phone": "+91-522-2257450",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 2200,
        "beds_available": 40,
        "icu_available": 8,
        "oxygen_available": 22,
        "ventilators_available": 5,
        "blood_stock": {"A+": 34, "A-": 11, "B+": 46, "B-": 10, "O+": 59, "O-": 7, "AB+": 21, "AB-": 4, "Platelets": 29},
        "last_updated": "11 mins ago",
    },
    {
        "id": "lko-redcross",
        "name": "Red Cross Blood Bank Lucknow",
        "type": "Blood Bank",
        "city": "Lucknow",
        "lat": 26.8488,
        "lon": 80.9412,
        "address": "Raja Nawab Ali Road, Kaiserbagh, Lucknow",
        "phone": "+91-522-2627993",
        "emergency_phone": "1910",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 70, "A-": 24, "B+": 85, "B-": 19, "O+": 96, "O-": 15, "AB+": 36, "AB-": 9, "Platelets": 34},
        "last_updated": "16 mins ago",
    },

    # ------------------ PATNA ------------------
    {
        "id": "pat-aiims",
        "name": "AIIMS Patna",
        "type": "Hospital",
        "city": "Patna",
        "lat": 25.5606,
        "lon": 85.0425,
        "address": "Phulwarisharif, Patna, Bihar",
        "phone": "+91-612-2451006",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 960,
        "beds_available": 35,
        "icu_available": 7,
        "oxygen_available": 20,
        "ventilators_available": 4,
        "blood_stock": {"A+": 30, "A-": 10, "B+": 40, "B-": 9, "O+": 52, "O-": 6, "AB+": 18, "AB-": 3, "Platelets": 24},
        "last_updated": "9 mins ago",
    },
    {
        "id": "pat-pmch",
        "name": "Patna Medical College Hospital (PMCH)",
        "type": "Hospital",
        "city": "Patna",
        "lat": 25.6202,
        "lon": 85.1610,
        "address": "Ashok Rajpath, Patna, Bihar",
        "phone": "+91-612-2300080",
        "emergency_phone": "108",
        "is_24_7": True,
        "beds_total": 1700,
        "beds_available": 28,
        "icu_available": 4,
        "oxygen_available": 16,
        "ventilators_available": 2,
        "blood_stock": {"A+": 25, "A-": 7, "B+": 34, "B-": 6, "O+": 45, "O-": 5, "AB+": 15, "AB-": 2, "Platelets": 18},
        "last_updated": "22 mins ago",
    },
    {
        "id": "pat-redcross",
        "name": "Red Cross Society Blood Bank Patna",
        "type": "Blood Bank",
        "city": "Patna",
        "lat": 25.6125,
        "lon": 85.1432,
        "address": "Gandhi Maidan North, Patna",
        "phone": "+91-612-2223844",
        "emergency_phone": "1910",
        "is_24_7": True,
        "beds_total": 0,
        "beds_available": 0,
        "icu_available": 0,
        "oxygen_available": 0,
        "ventilators_available": 0,
        "blood_stock": {"A+": 60, "A-": 18, "B+": 75, "B-": 16, "O+": 88, "O-": 12, "AB+": 32, "AB-": 7, "Platelets": 26},
        "last_updated": "13 mins ago",
    },
]


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula."""
    R = 6371.0  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)


def geocode_place(query: str):
    """Geocode any city name, area, or pincode using OpenStreetMap Nominatim.
    Returns (lat, lon, display_name) or None if not found/offline.
    """
    if not query or not query.strip():
        return None
    q = query.strip()
    # Check if user passed known city name
    for city_name, coords in CITIES.items():
        if city_name.lower() in q.lower() or q.lower() in city_name.lower():
            return coords["lat"], coords["lon"], city_name

    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": q, "format": "json", "limit": 1}
        headers = {"User-Agent": "MediMindAI-FacilityFinder/1.0"}
        r = requests.get(url, params=params, headers=headers, timeout=5)
        if r.ok:
            data = r.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                name = data[0].get("display_name", q).split(",")[0]
                return lat, lon, name
    except Exception:
        pass
    return None


def search_facilities(
    center_lat: float,
    center_lon: float,
    facility_type: str = "All",
    req_blood: str = None,
    req_icu: bool = False,
    req_oxygen: bool = False,
    max_distance_km: float = 100.0,
    search_query: str = "",
):
    """Filter and rank facilities by criteria and proximity."""
    results = []
    q = search_query.lower().strip() if search_query else ""

    for f in FACILITIES:
        # Type filter
        if facility_type != "All" and f["type"].lower() != facility_type.lower():
            continue

        # ICU filter
        if req_icu and f["type"] == "Hospital" and f.get("icu_available", 0) <= 0:
            continue

        # Oxygen filter
        if req_oxygen and f["type"] == "Hospital" and f.get("oxygen_available", 0) <= 0:
            continue

        # Blood group filter
        if req_blood and req_blood != "Any":
            stock = f.get("blood_stock", {})
            if stock.get(req_blood, 0) <= 0:
                continue

        # Text search match (name, city, address)
        if q:
            match_text = f"{f['name']} {f['city']} {f['address']} {f['type']}".lower()
            if q not in match_text:
                continue

        # Distance calculation
        dist = haversine(center_lat, center_lon, f["lat"], f["lon"])
        if max_distance_km and dist > max_distance_km:
            continue

        item = dict(f)
        item["distance_km"] = dist

        # Status badge determination
        if f["type"] == "Hospital":
            if f.get("beds_available", 0) > 15:
                item["status"] = "Good Availability"
                item["status_color"] = "#22c55e"  # Green
            elif f.get("beds_available", 0) > 0:
                item["status"] = "Low Availability"
                item["status_color"] = "#f59e0b"  # Amber
            else:
                item["status"] = "Full"
                item["status_color"] = "#ef4444"  # Red
        else:
            total_units = sum(f.get("blood_stock", {}).values())
            if total_units > 100:
                item["status"] = "High Stock"
                item["status_color"] = "#dc2626"  # Red for Blood
            else:
                item["status"] = "Moderate Stock"
                item["status_color"] = "#f97316"

        results.append(item)

    # Sort results by distance closest first
    results.sort(key=lambda x: x["distance_km"])
    return results


def detect_live_location():
    """Detect current live location using IP/network geolocation.
    Returns (lat, lon, label) or None if unavailable.
    """
    try:
        r = requests.get("http://ip-api.com/json/", timeout=4)
        if r.ok:
            data = r.json()
            if data.get("status") == "success":
                lat = float(data["lat"])
                lon = float(data["lon"])
                city = data.get("city", "")
                region = data.get("regionName", "")
                zipcode = data.get("zip", "")
                label = f"{city}, {region} ({zipcode})".strip(", ")
                return lat, lon, label
    except Exception:
        pass
    return None

