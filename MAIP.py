import extra_streamlit_components as stx
import streamlit as st
import requests
import datetime
from urllib.parse import quote

st.title("Malaria inhibitor prediction")
st.markdown(
    """ The malaria inhibitor prediction (MAIP) platform is the result of a public-private collaboration whose aim is to develop a consensus model for predicting blood stage malaria inhibition. Five Pharma and not-for-profit partners trained a model (using code developed by EMBL-EBI) on their private datasets. The resulting models were combined by EMBL-EBI and made available through this public prediction platform.

The work to develop this platform is described in full in the article [MAIP: A Prediction Platform for Predicting Blood-Stage Malaria Inhibitors](https://doi.org/10.1186/s13321-021-00487-2).

More information and details on the [input](https://chembl.gitbook.io/malaria-project/input-data-file) and [output](https://chembl.gitbook.io/malaria-project/output-file) format files are given [here](https://chembl.gitbook.io/malaria-project/).

One of our partners, the Medicines for [Malaria Venture (MMV)](https://www.mmv.org/mmv-open), is committed to supporting Open Innovation and taking drug discovery to the next level. Please [contact us](mailto:maip@mmv.org) if you would like to test a sample of any compounds that you identify using MAIP in MMV’s Plasmodium falciparum asexual blood stage assay. Terms and conditions are available on the MMV website. """
)

st.markdown(
    "Check the documentation [here](https://chembl.gitbook.io/malaria-project)."
)

@st.cache_resource(experimental_allow_widgets=True)
def get_cookie_manager():
    return stx.CookieManager()


cookie_manager = get_cookie_manager()


def run_predictions(file_content, file_name):
    data = {
        "standardise": True if standardise else False,
        "dl__ignore_cache": True if ignore_cache else False,
    }
    files = {"input1": file_content}

    res = requests.post(
        "https://www.ebi.ac.uk/chembl/interface_api/delayed_jobs/submit/mmv_job",
        data=data,
        files=files,
    ).json()
    cookie_manager.set(
        cookie=quote(f"{res['job_id']} | {file_name}"), val=str(datetime.datetime.now())
    )
    return res


def check_job_status(job_id):
    res_status = requests.get(
        f"https://www.ebi.ac.uk/chembl/interface_api/delayed_jobs/status/{job_id}"
    ).json()
    return res_status


with st.form(key="checkbox_form"):
    uploaded_file = st.file_uploader(
        "Upload a CSV file with a **id** and **smiles** columns", type="csv"
    )
    col1, col2 = st.columns(2)
    standardise = col1.checkbox("standardise")
    ignore_cache = col2.checkbox("ignore cache")
    submit_button = st.form_submit_button(label="Submit")


if uploaded_file is not None:
    if uploaded_file:
        res = run_predictions(uploaded_file.getvalue(), uploaded_file.name)
        job_id = res["job_id"]
        st.success(
            f"Job {job_id} submitted using {uploaded_file.name} file. Please check 'Browse jobs' section for results"
        )
