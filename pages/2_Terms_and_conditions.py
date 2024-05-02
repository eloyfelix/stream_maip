import streamlit as st

# Header
st.title("Terms and Conditions")

# Text content
st.write(
    "The malaria inhibitor prediction platform is provided 'AS IS', without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the use of the platform."
)

st.write("**Input and output files retention policy**")
st.write(
    "Input and output files are stored on the internal EMBL-EBI servers for seven days after the job finishes. This enables the results for any resubmitted jobs to be rapidly retrieved. They are subjected to no processing or analysis other than is required to run the MAIP job. Any queries about the MAIP file retention policy should be sent to the ChEMBL email helpdesk."
)
