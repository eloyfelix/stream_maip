import extra_streamlit_components as stx
import streamlit as st
from io import BytesIO
import requests
import pandas as pd
import plotly.graph_objs as go
import time

st.set_option("deprecation.showPyplotGlobalUse", False)

st.title("Malaria inhibitor prediction")
st.markdown(""" The malaria inhibitor prediction (MAIP) platform is the result of a public-private collaboration whose aim is to develop a consensus model for predicting blood stage malaria inhibition. Five Pharma and not-for-profit partners trained a model (using code developed by EMBL-EBI) on their private datasets. The resulting models were combined by EMBL-EBI and made available through this public prediction platform.

The work to develop this platform is described in full in the article [MAIP: A Prediction Platform for Predicting Blood-Stage Malaria Inhibitors](https://doi.org/10.1186/s13321-021-00487-2).

More information and details on the [input](https://chembl.gitbook.io/malaria-project/input-data-file) and [output](https://chembl.gitbook.io/malaria-project/output-file) format files are given [here](https://chembl.gitbook.io/malaria-project/).

One of our partners, the Medicines for [Malaria Venture (MMV)](https://www.mmv.org/mmv-open), is committed to supporting Open Innovation and taking drug discovery to the next level. Please [contact us](mailto:maip@mmv.org) if you would like to test a sample of any compounds that you identify using MAIP in MMV’s Plasmodium falciparum asexual blood stage assay. Terms and conditions are available on the MMV website. """)

st.markdown(
    "Check the documentation [here](https://chembl.gitbook.io/malaria-project)."
)


def get_cookie_manager():
    return stx.CookieManager()


cookie_manager = get_cookie_manager()


def generate_file_content(df):
    # Convert DataFrame to CSV
    csv = df.to_csv(index=False)

    # Create BytesIO object to hold the CSV data
    bytes_io = BytesIO()
    bytes_io.write(csv.encode())
    bytes_io.seek(0)  # Move the cursor to the start of the stream

    return bytes_io


def run_predictions(file_content):
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

    cookie_manager.set(cookie="job_id", val=res["job_id"])
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


job_id = cookie_manager.get(cookie="job_id")
if uploaded_file is not None or job_id is not None:
    if uploaded_file:
        res = run_predictions(uploaded_file.getvalue())
        job_id = res["job_id"]
    job_status = check_job_status(job_id)
    while job_status["status"] != "FINISHED":
        job_status = check_job_status(job_id)
        time.sleep(2)

    out_files = job_status["output_files_urls"]

    st.markdown(f"job id: `{job_id}`")
    st.markdown(
        f"Download the predictions [here](https://{out_files['predictions.csv']})."
    )

    # Provided data
    data = requests.get(f"https://{out_files['hist_data.json']}").json()

    # Extracting bins and frequencies
    bins = [round(item[0]) for item in data["values"]]
    frequencies = [item[1] for item in data["values"]]

    # Creating a Plotly histogram trace
    trace = go.Bar(x=bins, y=frequencies, marker=dict(color="blue"))

    # Adding vertical lines
    vertical_lines_values = (
        (data["t1"], "1% threshold"),
        (data["t10"], "10% threshold"),
        (data["t50"], "50% threshold"),
    )
    shapes = [
        dict(
            type="line",
            xref="x",
            yref="paper",
            x0=value,
            y0=0,
            x1=value,
            y1=1,
            line=dict(color="red", width=2, dash="dash"),
        )
        for value, _ in vertical_lines_values
    ]

    # Adding text annotations for the vertical lines
    annotations = [
        dict(
            x=value,
            y=max(frequencies),
            xref="x",
            yref="y",
            text=text,
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40,
        )
        for value, text in vertical_lines_values
    ]

    # Creating the layout
    layout = go.Layout(
        title="This is the distribution plot of your predicted scores",
        xaxis=dict(title="Model score"),
        yaxis=dict(title="Proportion of data"),
        shapes=shapes,
        annotations=annotations,
    )

    # Creating the figure
    fig = go.Figure(data=[trace], layout=layout)

    # Plotting the figure
    st.plotly_chart(fig)

    data = {
        "Performance metrics": ["ROC AUC score", "EF[1%]", "EF[10%]", "EF[50%]"],
        "MMV test set": [0.67, "3.5 (60)", "2.1 (41)", "1.4 (23)"],
        "PubChem": [0.69, "7.0 (56)", "2.8 (47)", "1.5 (34)"],
        "St. Jude Screening Set": [0.81, "12.1 (71)", "4.8 (36)", "1.8 (15)"],
    }

    st.write("**Results we obtained on three different validation sets**")
    st.markdown(
        "[Further details](https://chembl.gitbook.io/malaria-project/using-maip-results)"
    )

    # Create DataFrame
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True)
