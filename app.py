import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile
import io
import os

# Set up Streamlit layout
st.set_page_config(page_title="Enhanced Graph Generator", layout="wide")

# Tabs for different sections
tabs = st.tabs(["Input Data", "Graph Settings", "Output Files"])

# Data storage for multiple datasets and graph configurations
data_files = []
graph_configurations = []
graphs = []

# Input Data Tab
with tabs[0]:
    st.header("Input Data")

    # Sidebar for input options
    with st.sidebar:
        st.subheader("Data Input Options")
        st.write("Upload one or multiple data files to be used in the graphs.")
        
        # File uploader for multiple files
        uploaded_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)

        # Process each uploaded file
        for uploaded_file in uploaded_files:
            data = pd.read_csv(uploaded_file)
            data_files.append((uploaded_file.name, data))
            st.write(f"Data preview for `{uploaded_file.name}`")
            st.data_editor(data, num_rows="dynamic")

# Graph Settings Tab
with tabs[1]:
    st.header("Graph Settings")

    # Sidebar for graph configuration
    with st.sidebar:
        st.subheader("Graph Configuration")

        # User selects a dataset to configure graph settings for
        dataset_names = [name for name, _ in data_files]
        selected_dataset_name = st.selectbox("Select Dataset for Graph", dataset_names)
        selected_data = next((data for name, data in data_files if name == selected_dataset_name), None)

        if selected_data is not None:
            # Graph type selection
            graph_type = st.selectbox("Choose Graph Type", ["Line", "Scatter", "Bar", "Histogram", "Box"])
            
            # Axis selection
            x_axis = st.selectbox("X-Axis", selected_data.columns)
            y_axis = st.selectbox("Y-Axis", selected_data.columns)

            # Additional settings
            graph_title = st.text_input("Graph Title", value=f"{graph_type} Plot of {x_axis} vs {y_axis}")
            color_col = st.selectbox("Color Column (optional)", [None] + list(selected_data.columns))

            # Save configuration
            graph_configurations.append({
                "dataset_name": selected_dataset_name,
                "graph_type": graph_type,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "graph_title": graph_title,
                "color_col": color_col
            })

            # Preview the graph
            if st.button("Generate Preview"):
                fig = None
                if graph_type == "Line":
                    fig = px.line(selected_data, x=x_axis, y=y_axis, title=graph_title, color=color_col)
                elif graph_type == "Scatter":
                    fig = px.scatter(selected_data, x=x_axis, y=y_axis, title=graph_title, color=color_col)
                elif graph_type == "Bar":
                    fig = px.bar(selected_data, x=x_axis, y=y_axis, title=graph_title, color=color_col)
                elif graph_type == "Histogram":
                    fig = px.histogram(selected_data, x=x_axis, title=graph_title, color=color_col)
                elif graph_type == "Box":
                    fig = px.box(selected_data, x=x_axis, y=y_axis, title=graph_title, color=color_col)
                
                if fig:
                    graphs.append((f"{graph_title}.png", fig))
                    st.plotly_chart(fig)

# Output Files Tab
with tabs[2]:
    st.header("Output Files")

    # Right sidebar for output options
    with st.sidebar:
        st.subheader("Output Options")
        
        # File format selection
        output_format = st.selectbox("Select Output Format", ["PNG", "PDF"])
        
        # Generate ZIP file option
        zip_output = st.checkbox("Download as ZIP file")

    # Show generated graphs
    for file_name, fig in graphs:
        st.write(f"Graph: {file_name}")
        st.plotly_chart(fig)

    # Download options
    if st.button("Download Files"):
        # Buffer for ZIP file
        buffer = io.BytesIO()

        # Generate individual files or ZIP
        with zipfile.ZipFile(buffer, "w") as zipf:
            for file_name, fig in graphs:
                # Save each graph to a buffer as per the selected format
                img_buffer = io.BytesIO()
                fig.write_image(img_buffer, format=output_format.lower())
                img_buffer.seek(0)
                
                if zip_output:
                    # Add to ZIP file
                    zipf.writestr(f"{file_name}.{output_format.lower()}", img_buffer.read())
                else:
                    # Direct download of each file
                    st.download_button(
                        label=f"Download {file_name}.{output_format.lower()}",
                        data=img_buffer,
                        file_name=f"{file_name}.{output_format.lower()}",
                        mime=f"image/{output_format.lower()}"
                    )

        if zip_output:
            # Provide ZIP download button
            buffer.seek(0)
            st.download_button(
                label="Download All as ZIP",
                data=buffer,
                file_name="graphs.zip",
                mime="application/zip"
            )
