from flask import Flask, render_template, request
import joblib
import sqlite3
import os

app = Flask(__name__)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():

    base_dir = os.path.dirname(os.path.abspath(__file__))

    database_dir = os.path.join(base_dir, "database")

    os.makedirs(database_dir, exist_ok=True)

    db_path = os.path.join(database_dir, "hospital.db")

    conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row

    return conn


# ==================================================
# LOAD MODEL
# ==================================================

base_dir = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(
    base_dir,
    "hospital_readmission_model.pkl"
)

model_data = joblib.load(model_path)

model = model_data["model"]

feature_names = model_data["features"]

final_threshold = model_data["threshold"]


print("==============================================")
print("MODEL INFORMATION")
print("==============================================")
print("Model type:", type(model))
print("Number of features:", len(feature_names))
print("Final threshold:", final_threshold)

print()
print("FEATURES USED BY THE MODEL:")

for i, feature in enumerate(feature_names, start=1):
    print(i, ":", feature)

print("==============================================")


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    probability_percent = None

    if request.method == "POST":

        # ------------------------------------------
        # NUMERICAL VALUES
        # ------------------------------------------

        admission_type_id = int(
            request.form["admission_type_id"]
        )

        time_in_hospital = int(
            request.form["time_in_hospital"]
        )

        num_lab_procedures = int(
            request.form["num_lab_procedures"]
        )

        num_procedures = int(
            request.form["num_procedures"]
        )

        num_medications = int(
            request.form["num_medications"]
        )

        number_outpatient = int(
            request.form["number_outpatient"]
        )

        number_emergency = int(
            request.form["number_emergency"]
        )

        number_inpatient = int(
            request.form["number_inpatient"]
        )

        number_diagnoses = int(
            request.form["number_diagnoses"]
        )

        # ------------------------------------------
        # DROPDOWN VALUES
        # ------------------------------------------

        race = request.form["race"]

        gender = request.form["gender"]

        age = request.form["age"]

        max_glu_serum = request.form["max_glu_serum"]

        A1Cresult = request.form["A1Cresult"]

        insulin = request.form["insulin"]

        change = request.form["change"]

        diabetesMed = request.form["diabetesMed"]

        # ------------------------------------------
        # START ALL FEATURES WITH 0
        # ------------------------------------------

        data = {
            feature: 0
            for feature in feature_names
        }

        # ------------------------------------------
        # NUMERICAL FEATURES
        # ------------------------------------------

        data["admission_type_id"] = admission_type_id

        data["time_in_hospital"] = time_in_hospital

        data["num_lab_procedures"] = num_lab_procedures

        data["num_procedures"] = num_procedures

        data["num_medications"] = num_medications

        data["number_outpatient"] = number_outpatient

        data["number_emergency"] = number_emergency

        data["number_inpatient"] = number_inpatient

        data["number_diagnoses"] = number_diagnoses

        # ------------------------------------------
        # RACE
        # ------------------------------------------

        if race == "AfricanAmerican":

            data["race_AfricanAmerican"] = 1

        elif race == "Asian":

            data["race_Asian"] = 1

        elif race == "Caucasian":

            data["race_Caucasian"] = 1

        elif race == "Hispanic":

            data["race_Hispanic"] = 1

        elif race == "Other":

            data["race_Other"] = 1

        # ------------------------------------------
        # GENDER
        # ------------------------------------------

        if gender == "Male":

            data["gender_Male"] = 1

        elif gender == "Unknown/Invalid":

            data["gender_Unknown/Invalid"] = 1

        # Female is the reference category.

        # ------------------------------------------
        # AGE
        # ------------------------------------------

        if age == "[10-20)":

            data["age_[10-20)"] = 1

        elif age == "[20-30)":

            data["age_[20-30)"] = 1

        elif age == "[30-40)":

            data["age_[30-40)"] = 1

        elif age == "[40-50)":

            data["age_[40-50)"] = 1

        elif age == "[50-60)":

            data["age_[50-60)"] = 1

        elif age == "[60-70)":

            data["age_[60-70)"] = 1

        elif age == "[70-80)":

            data["age_[70-80)"] = 1

        elif age == "[80-90)":

            data["age_[80-90)"] = 1

        elif age == "[90-100)":

            data["age_[90-100)"] = 1

        # ------------------------------------------
        # MAXIMUM GLUCOSE SERUM
        # ------------------------------------------

        if max_glu_serum == ">300":

            data["max_glu_serum_>300"] = 1

        elif max_glu_serum == "Norm":

            data["max_glu_serum_Norm"] = 1

        # ------------------------------------------
        # A1C RESULT
        # ------------------------------------------

        if A1Cresult == ">8":

            data["A1Cresult_>8"] = 1

        elif A1Cresult == "Norm":

            data["A1Cresult_Norm"] = 1

        # ------------------------------------------
        # INSULIN
        # ------------------------------------------

        if insulin == "No":

            data["insulin_No"] = 1

        elif insulin == "Steady":

            data["insulin_Steady"] = 1

        elif insulin == "Up":

            data["insulin_Up"] = 1

        # Down is the reference category.

        # ------------------------------------------
        # CHANGE IN MEDICATION
        # ------------------------------------------

        if change == "No":

            data["change_No"] = 1

        # ------------------------------------------
        # DIABETES MEDICATION
        # ------------------------------------------

        if diabetesMed == "Yes":

            data["diabetesMed_Yes"] = 1

        # ------------------------------------------
        # ARRANGE FEATURES IN TRAINING ORDER
        # ------------------------------------------

        input_data = [
            data[feature]
            for feature in feature_names
        ]

        # ------------------------------------------
        # GET PREDICTION PROBABILITY
        # ------------------------------------------

        probability = model.predict_proba(
            [input_data]
        )[0][1]

        # ------------------------------------------
        # APPLY FINAL THRESHOLD
        # ------------------------------------------

        prediction = int(
            probability >= final_threshold
        )

        # ------------------------------------------
        # DISPLAY RESULT
        # ------------------------------------------

        if prediction == 1:

            result = "High Risk of Readmission"

        else:

            result = "Low Risk of Readmission"

        probability_percent = round(
            probability * 100,
            2
        )

        # ------------------------------------------
        # SAVE PATIENT DATA AND PREDICTION
        # ------------------------------------------

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO patient_predictions (
                admission_type_id,
                time_in_hospital,
                num_lab_procedures,
                num_procedures,
                num_medications,
                number_outpatient,
                number_emergency,
                number_inpatient,
                number_diagnoses,
                race,
                gender,
                age,
                max_glu_serum,
                A1Cresult,
                insulin,
                change_medication,
                diabetesMed,
                prediction,
                probability
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            admission_type_id,
            time_in_hospital,
            num_lab_procedures,
            num_procedures,
            num_medications,
            number_outpatient,
            number_emergency,
            number_inpatient,
            number_diagnoses,
            race,
            gender,
            age,
            max_glu_serum,
            A1Cresult,
            insulin,
            change,
            diabetesMed,
            result,
            probability_percent
        ))

        conn.commit()

        conn.close()

    # ------------------------------------------
    # DISPLAY WEB PAGE
    # ------------------------------------------

    return render_template(
        "index.html",
        result=result,
        probability=probability_percent
    )


# ==================================================
# PATIENT HISTORY PAGE
# ==================================================

@app.route("/history")
def history():

    conn = get_db_connection()

    patients = conn.execute("""
        SELECT *
        FROM patient_predictions
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    return render_template(
        "history.html",
        patients=patients
    )


# ==================================================
# DELETE ONE HISTORY RECORD
# ==================================================

@app.route("/delete/<int:patient_id>", methods=["POST"])
def delete_patient(patient_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM patient_predictions WHERE id = ?",
        (patient_id,)
    )

    conn.commit()

    conn.close()

    return """
    <script>
        window.location.href = "/history";
    </script>
    """


# ==================================================
# DELETE ALL HISTORY
# ==================================================

@app.route("/delete_all_history", methods=["POST"])
def delete_all_history():

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM patient_predictions"
    )

    conn.commit()

    conn.close()

    return """
    <script>
        window.location.href = "/history";
    </script>
    """


# ==================================================
# START FLASK
# ==================================================

if __name__ == "__main__":
      
      app.run(debug=True)
