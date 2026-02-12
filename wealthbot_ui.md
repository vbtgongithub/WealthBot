# WealthBot: Production UI Code Generation Prompt

**Role:** Act as a **Lead Product Designer** and **Senior React Native Engineer** at a top-tier fintech company (similar to Cred, Monzo, or Revolut). You specialize in "Neobanking" aesthetics—clean, minimalist, dark-mode first, and highly interactive.

**Project Context:**
We are building **"WealthBot,"** a predictive personal finance app for students in India.
* **Core Value:** Unlike apps that just show a static balance, we use an XGBoost model to predict a **"Safe-to-Spend"** limit for the day, accounting for upcoming bills ("Shadow Obligations").
* **Target Audience:** Gen Z students (UPI-heavy, mobile-first, dark mode users).

**Tech Stack (Strict Constraints):**
* **Framework:** React Native (with **Expo Router** for file-based routing).
* **Styling:** **NativeWind** (Tailwind CSS for React Native).
* **State Management:** **Zustand** (for global store).
* **Icons:** `lucide-react-native`.
* **Charts:** `react-native-gifted-charts` (for high-performance visualizations).
* **Fonts:** Inter or similar variable font (assumed loaded).

---

## **Task Requirements**

Generate the **Production-Ready React Native Code** for the following 4 Critical Screens. 

**Output Structure:**
1.  **`constants/data.ts`**: A robust mock data file with realistic Indian transaction data (₹ currency, UPI apps like Swiggy, Zepto, Uber).
2.  **`store/userStore.ts`**: A simple Zustand store to manage the "Safe-to-Spend" number and transactions.
3.  **Screen Files**: Provide the full code for each screen listed below.

---

### **Screen 1: The "Safe-to-Spend" Dashboard (Home)**
**File Path:** `app/(tabs)/index.tsx`
**Vibe:** Futuristic, confident, clutter-free.
**Key Elements:**
1.  **Hero Gauge:** A large, animated semi-circular speedometer showing the **"Safe-to-Spend"** amount (e.g., ₹850 left).
    * *Visual Logic:* Color scales from Red (<₹200) to Yellow to Green (>₹800).
2.  **Contextual Pill:** A text pill below the gauge saying *"Safe until Friday"* (implying the model knows payday is Friday).
3.  **Quick Actions:** A horizontal scroll of "Frequent" actions (Scan QR, Add Cash).
4.  **Recent Activity:** A condensed list of the last 3 transactions with category icons (e.g., specific icons for Food, Transport).

### **Screen 2: The "Smart" Transaction List**
**File Path:** `app/(tabs)/transactions.tsx`
**Vibe:** Data-rich but scannable.
**Key Elements:**
1.  **Smart Grouping:** Transactions grouped by headers: "Today," "Yesterday," and "This Week."
2.  **Visual Tags:** Auto-categorized tags (e.g., `#Food`, `#Travel`) that look like distinct colored pills.
3.  **Search Bar:** A prominent search input ("Search 'Swiggy' or 'Last Week'...").
4.  **Edit Action:** A visual cue (pencil icon) on list items to edit a category if the AI prediction was wrong.

### **Screen 3: The "Leakage Hunter" (Analytics)**
**File Path:** `app/(tabs)/analytics.tsx`
**Vibe:** Insightful, actionable (not just boring pie charts).
**Key Elements:**
1.  **Subscription Radar:** A distinct card highlighting recurring payments (e.g., *"Netflix • ₹649 • Due in 2 days"*).
2.  **Spending Velocity:** A line chart comparing "This Month's Spending" vs. "Last Month."
3.  **The "Ouch" Metric:** A highlight card showing the biggest unnecessary expense category (e.g., *"You spent ₹4,000 on Cafe Coffee Day"*).

### **Screen 4: The "Vault" & Data Manager (Settings)**
**File Path:** `app/(tabs)/settings.tsx`
**Vibe:** Secure, technical, trust-building.
**Key Elements:**
1.  **Magic Import Card:** A prominent area to **"Upload Bank Statement (PDF/CSV)"**. Include visual states for "Processing..." and "Success."
2.  **The Privacy Log:** A terminal-like list showing access logs to prove security (e.g., *"System accessed data at 10:42 AM - Encrypted"*). **(Crucial for academic demo)**.
3.  **Net Worth Input:** A simple manual field for "Total Investments" (e.g., ₹50,000) to include in the algorithm without complex API integration.
4.  **Developer Mode:** A toggle switch to "Show ML Confidence Scores."

---

## **Coding Guidelines**
* **Styling:** Use `className="..."` (NativeWind) for all styling.
* **Components:** Extract reusable parts (like `TransactionCard` or `Gauge`) if the code gets too long, but keep it within the same code block for easy copying.
* **Comments:** Add brief comments explaining *why* specific UX decisions were made (e.g., *"Used Emerald-500 for 'Safe' state to reduce user anxiety"*).