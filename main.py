import streamlit as st
import pyrebase
from google.cloud import firestore

ap_signup_version = "1.0.2"
signup_form_submitted = False

st.set_page_config(
    page_title=f"AlphaPredict Signup ({ap_signup_version})",
    page_icon=":chart_with_upwards_trend:",
    layout="centered",
    menu_items={
        'Get help': 'mailto:support@neuralbytes.net?subject=Need%20Help%20with%20AlphaPredict',
        'Report a bug': 'mailto:bugs@neuralbytes.net?subject=AlphaPredict%20Bug%20Report',
        'About': '''### The signup page for AlphaPredict: A professional stock market predictor and insight-provider, with charts and company details. \n
        https://alphapredict.neuralbytes.net'''
    }
)

st.title("AlphaPredict Signup Page")
st.write("[Help improve AlphaPredict](mailto:feedback@neuralbytes.net?subject=AlphaPredict%20Feedback)")

firebaseConfig = {
    'apiKey': st.secrets.firebaseConfig['apiKey'],
    'authDomain': st.secrets.firebaseConfig['authDomain'],
    'databaseURL': st.secrets.firebaseConfig['databaseURL'],
    'projectId': st.secrets.firebaseConfig['projectId'],
    'storageBucket': st.secrets.firebaseConfig['storageBucket'],
    'messagingSenderId': st.secrets.firebaseConfig['messagingSenderId'],
    'appId': st.secrets.firebaseConfig['appId'],
    'measurementId': st.secrets.firebaseConfig['measurementId']
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firestore.Client.from_service_account_json(".streamlit/alphapredict-firebase-key.json")


def sign_up():
    """Returns `True` if the user had a correct password."""

    def signup_form():
        st.header("Signup Form")
        with st.form("Credentials"):
            st.session_state["first_name"] = st.text_input("First Name")
            st.session_state["last_name"] = st.text_input("Last Name")
            st.session_state["email"] = st.text_input("Email")
            st.session_state["password"] = st.text_input("Password", type="password")
            st.session_state["user_plan"] = st.selectbox("Choose a Plan", ["Pro", "Max"])
            st.session_state["user_paid"] = st.selectbox("Already Paid?", ["Yes", "No"])
            st.form_submit_button("Sign up", on_click=password_entered)
            st.caption("⬆️ Press it twice (not rapidly, though)")
        with st.expander("ℹ️ Pricing"):
            st.write("""AlphaPredictPro - Uses GPT-3.5 and is optimized for speed, but may be less accurate. - $7/month""")
            st.write("AlphaPredictMax - Uses GPT-4o for more detailed, logical, and accurate insights - $15/month")

    def password_entered():
        form_submitted = True
        try:
            signup = auth.create_user_with_email_and_password(st.session_state["email"], st.session_state["password"])
            auth.send_email_verification(signup['idToken'])
            print(signup)
            st.session_state["password_correct"] = True
            doc_ref = db.collection("users").document(st.session_state["email"])
            doc = doc_ref.get()
            if st.session_state["user_paid"] == "Yes":
                paid_status = True
            else:
                paid_status = False
            doc_ref.set({
                "FirstName": st.session_state["first_name"],
                "LastName": st.session_state["last_name"],
                "Paid": paid_status,
                "Plan": st.session_state["user_plan"]
            })
            del st.session_state["first_name"]
            del st.session_state["last_name"]
            st.session_state["user_name"] = doc.to_dict()["FirstName"] + " " + doc.to_dict()["LastName"]
            st.session_state["user_plan"] = doc.to_dict()["Plan"]
            st.session_state["user_paid"] = doc.to_dict()["Paid"]
        except Exception as e:
            return

    signup_form()
    if not signup_form_submitted:
        return False

if not sign_up():
    st.stop()
