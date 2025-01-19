import streamlit as st
import pandas as pd
import numpy as np

class EcommerceValidator:
    def __init__(self):
        self.df = None
        self.errors = []
        self.summary = {}

    def load_excel(self, uploaded_file):
        try:
            self.df = pd.read_excel(uploaded_file)
            return True
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return False

    def validate_prices_and_tax(self):
        """Validate MAP vs MRP and tax rates row by row"""
        for index, row in self.df.iterrows():
            row_num = index + 2  # Excel row numbers start at 1 and header is row 1
            
            try:
                # Clean and convert price values
                map_price = float(str(row['MAP']).replace(',', '').replace('₹', '').strip())
                mrp = float(str(row['MRP (O)']).replace(',', '').replace('₹', '').strip())
                sale_price = float(str(row['Sale Price (inc tax)']).replace(',', '').replace('₹', '').strip())
                
                # Handle tax rate format (both 18% and 0.18 formats)
                tax_str = str(row['Tax Rate']).replace('%', '').strip()
                tax_rate = float(tax_str)
                if tax_rate < 1:  # If tax is in decimal format (0.18)
                    tax_rate = tax_rate * 100  # Convert to percentage (18)

                # Check MAP vs MRP only
                if map_price >= mrp:
                    self.errors.append({
                        'Row': row_num,
                        'Type': 'Price Error',
                        'Error': f"MAP (₹{map_price:,.2f}) is greater than or equal to MRP (₹{mrp:,.2f})"
                    })

                # Check Tax Rate
                expected_tax = 18 if sale_price > 999 else 12
                if int(tax_rate) != expected_tax:  # Convert to int to ignore decimal places
                    self.errors.append({
                        'Row': row_num,
                        'Type': 'Tax Error',
                        'Error': f"Incorrect tax rate {int(tax_rate)}% for Sale Price ₹{sale_price:,.2f} (should be {expected_tax}%)"
                    })

            except Exception as e:
                self.errors.append({
                    'Row': row_num,
                    'Type': 'Data Error',
                    'Error': f"Invalid data in row: {str(e)}"
                })

    def validate(self):
        """Run all validations"""
        self.errors = []  # Reset errors
        
        # Validate prices and tax
        self.validate_prices_and_tax()

        # Prepare summary
        total_rows = len(self.df)
        invalid_rows = len(set(error['Row'] for error in self.errors))
        
        self.summary = {
            'Total Rows': total_rows,
            'Valid Rows': total_rows - invalid_rows,
            'Invalid Rows': invalid_rows
        }

def main():
    # Page config with custom theme
    st.set_page_config(
        page_title="E-commerce Excel Validator",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS with text logo styling
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stAlert {
            padding: 1rem;
            border-radius: 8px;
        }
        .upload-box {
            border: 2px dashed #4CAF50;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            margin: 2rem 0;
        }
        .header-container {
            background-color: #f1f3f4;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            position: relative;
        }
        .logo-text {
            position: absolute;
            top: 1rem;
            left: 2rem;
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header Section with Text Logo
    st.markdown("""
        <div class="header-container">
            <div class="logo-text">GridRay</div>
            <h1>📊 E-commerce Excel Validator</h1>
            <p>Upload your product listing Excel file to validate pricing and tax rules</p>
        </div>
    """, unsafe_allow_html=True)

    # Create two columns for layout
    col1, _ = st.columns([1, 0.01])  # Changed from [2, 1] to [1, 0.01]

    with col1:
        # File Upload Section
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drag and drop your Excel file here",
            type=['xlsx', 'xls'],
            help="Upload an Excel file (.xlsx or .xls)"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        validator = EcommerceValidator()
        
        if validator.load_excel(uploaded_file):
            st.success(f"✅ Successfully loaded Excel file with {len(validator.df)} rows")

            # Tabs for different sections
            tab1, tab2, tab3 = st.tabs(["📊 Data Preview", "🔍 Validation Results", "📈 Summary"])

            with tab1:
                st.dataframe(validator.df, use_container_width=True)

            with tab2:
                # Run validation
                validator.validate()

                if validator.errors:
                    st.error("❌ Validation Errors Found:")
                    errors_df = pd.DataFrame(validator.errors)
                    errors_df = errors_df.sort_values('Row')
                    
                    # Style the error dataframe
                    st.dataframe(
                        errors_df,
                        use_container_width=True,
                        column_config={
                            "Row": st.column_config.NumberColumn(
                                "Row",
                                help="Excel row number"
                            ),
                            "Type": st.column_config.TextColumn(
                                "Error Type",
                                help="Type of validation error"
                            ),
                            "Error": st.column_config.TextColumn(
                                "Error Description",
                                help="Detailed error message"
                            )
                        }
                    )
                else:
                    st.success("✅ No validation errors found!")

            with tab3:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", validator.summary['Total Rows'])
                with col2:
                    st.metric("Valid Rows", validator.summary['Valid Rows'])
                with col3:
                    st.metric(
                        "Invalid Rows",
                        validator.summary['Invalid Rows'],
                        delta=f"-{validator.summary['Invalid Rows']}" if validator.summary['Invalid Rows'] > 0 else None,
                        delta_color="inverse"
                    )

    # Footer
    st.markdown("""
        <div style='margin-top: 3rem; text-align: center; color: #666;'>
            <hr>
            <p>Upload your Excel file to validate pricing and tax rules. The validator will check MAP vs MRP relationships and tax rates.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()