import extra_streamlit_components as stx
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
import time
from urllib.parse import unquote


st.title("Check results of submitted jobs")

@st.cache_resource(experimental_allow_widgets=True)
def get_cookie_manager():
    return stx.CookieManager()


cookie_manager = get_cookie_manager()


def check_job_status(job_id):
    res_status = requests.get(
        f"https://www.ebi.ac.uk/chembl/interface_api/delayed_jobs/status/{job_id}"
    ).json()
    return res_status


jobs = {}
for key, value in cookie_manager.get_all().items():
    key = unquote(key)
    if key.startswith("MMV-"):
        jobs[key] = f"{key} | {value}"
selected_option = st.selectbox("Select a job", jobs)

with st.spinner("Job still running..."):
    job_id = None
    if selected_option:
        job_id = selected_option.split("|")[0].strip()
    if job_id is not None:
        job_status = check_job_status(job_id)
        while job_status["status"] != "FINISHED":
            job_status = check_job_status(job_id)
            time.sleep(2)

        out_files = job_status["output_files_urls"]

        # st.markdown(f"job id: `{job_id}`")
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
