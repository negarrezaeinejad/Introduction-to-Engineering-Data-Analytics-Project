# Introduction to Engineering Data Analytics - Group 34 Final Project

## Project Overview
This repository contains the final submission for **Case Study 34 - Vehicle Recall Analysis**. As Quality Data Engineers for a fictitious automobile manufacturer, our objective was to identify **OEM1 Type11** vehicles equipped with defective **K1DI1** diesel engine control units produced between 18.10.2011 and 05.12.2013. 

The project encompasses a complete data analytics workflow:
1. **Data Integration & Preparation:** Merging supply chain, production, and parts-list data to identify affected vehicles.
2. **Geospatial Analysis:** Mapping vehicle registrations to compute proximity to major German cities with diesel driving bans.
3. **Interactive Dashboard:** A comprehensive Streamlit web application providing stakeholders with executive overviews, interactive maps, supply chain analytics, and vehicle lifecycle traces.

## Repository Structure
This submission strictly adheres to the requested folder structure. **Note:** Original raw datasets have been deliberately excluded from the `data/` folder as per the submission guidelines.

```text
SoSe26_Case_Study_Group_34/
│
├── additional_files/                           # Screenshots of the WebApp and supplementary files
├── data/
│   └── SoSe26_Case_Study_finalData_Group_34.csv # The final cleaned and processed dataset for the app
├── www/
│   └── logo.png                                # Department of Quality Science / Custom Logo
│
├── SoSe26_Case_Study_Group_34.ipynb            # Main Data Analysis Jupyter Notebook
├── SoSe26_Case_Study_Group_34.html             # HTML export of the Main Data Analysis Notebook
├── SoSe26_General_Tasks_Group_34.ipynb         # General Tasks Jupyter Notebook
├── SoSe26_General_Tasks_Group_34.html          # HTML export of the General Tasks Notebook
├── SoSe26_Case_Study_App_Group_34.py           # Streamlit Web Application script
└── README.md                                   # Project documentation and setup instructions

```

## How to Run the Web Application

The interactive dashboard is built using Streamlit. To ensure complete reproducibility on any machine without package conflicts, please follow these steps to run the application using Python's built-in virtual environment (`venv`).

### 1. Open Terminal and Navigate to the Project Folder

Ensure your terminal is operating inside the root directory of this submission (`SoSe26_Case_Study_Group_34`).

### 2. Create a Virtual Environment

Run the following command to create a fresh, isolated Python environment named `app_env`:

```bash
python3 -m venv app_env

```

### 3. Activate the Virtual Environment

Activate the environment so that all installations remain contained within this folder:

```bash
source app_env/bin/activate

```

*(You should now see `(app_env)` at the beginning of your terminal prompt.)*

### 4. Install Required Packages

Install Streamlit, Pandas, and Plotly using pip:

```bash
pip install streamlit pandas plotly

```

### 5. Launch the Dashboard

Run the Streamlit application script:

```bash
streamlit run SoSe26_Case_Study_App_Group_34.py

```

The terminal will spin up a local server, and the dashboard will automatically open in your default web browser (typically at `http://localhost:8501`).

---

**Data Path Note:** The Streamlit application (`SoSe26_Case_Study_App_Group_34.py`) uses relative file paths. It will automatically look for the required dataset (`SoSe26_Case_Study_finalData_Group_34.csv`) inside the `data/` folder, ensuring it runs seamlessly upon extraction.