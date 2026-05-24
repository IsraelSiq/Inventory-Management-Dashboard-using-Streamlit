import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}

.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    background-color: #1f77b4;
    color: white;
    font-weight: bold;
}

.stDataFrame {
    border-radius: 10px;
}

.metric-card {
    padding: 20px;
    border-radius: 12px;
    background-color: white;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(
        columns=[
            "Product ID",
            "Product Name",
            "Category",
            "Price",
            "Quantity",
            "Supplier",
            "Last Updated"
        ]
    )

# ---------------- HEADER ----------------
st.title("📦 Smart Inventory Management System")
st.markdown("### Manage Products, Stock & Inventory Efficiently")

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio(
    "📌 Navigation",
    [
        "Dashboard",
        "Add Product",
        "Update Stock",
        "Search Product",
        "Remove Product",
        "Inventory Report",
        "Analytics"
    ]
)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":

    st.subheader("📊 Inventory Dashboard")

    total_products = len(st.session_state.inventory)

    total_stock = (
        st.session_state.inventory["Quantity"].sum()
        if not st.session_state.inventory.empty else 0
    )

    total_value = (
        (
            st.session_state.inventory["Price"]
            * st.session_state.inventory["Quantity"]
        ).sum()
        if not st.session_state.inventory.empty else 0
    )

    low_stock = (
        len(
            st.session_state.inventory[
                st.session_state.inventory["Quantity"] < 5
            ]
        )
        if not st.session_state.inventory.empty else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📦 Products", total_products)
    col2.metric("📊 Total Stock", total_stock)
    col3.metric("💰 Inventory Value", f"₹ {total_value:,.2f}")
    col4.metric("⚠ Low Stock", low_stock)

    st.markdown("---")

    if not st.session_state.inventory.empty:
        st.subheader("📋 Recent Inventory")
        st.dataframe(
            st.session_state.inventory,
            use_container_width=True
        )
    else:
        st.info("Inventory is currently empty.")

# ---------------- ADD PRODUCT ----------------
elif menu == "Add Product":

    st.subheader("➕ Add New Product")

    with st.form("add_product_form"):

        col1, col2 = st.columns(2)

        with col1:
            product_id = st.text_input("Product ID")
            product_name = st.text_input("Product Name")
            category = st.selectbox(
                "Category",
                ["Electronics", "Food", "Clothing", "Furniture", "Other"]
            )

        with col2:
            price = st.number_input(
                "Price",
                min_value=0.0,
                format="%.2f"
            )

            quantity = st.number_input(
                "Quantity",
                min_value=0,
                step=1
            )

            supplier = st.text_input("Supplier Name")

        submit = st.form_submit_button("Add Product")

        if submit:

            if (
                product_id.strip() == ""
                or product_name.strip() == ""
                or supplier.strip() == ""
            ):
                st.error("❌ All fields are required")

            elif product_id in st.session_state.inventory["Product ID"].values:
                st.error("❌ Product ID already exists")

            elif price <= 0:
                st.error("❌ Price must be greater than 0")

            elif quantity <= 0:
                st.error("❌ Quantity must be greater than 0")

            else:

                new_row = pd.DataFrame([{
                    "Product ID": product_id,
                    "Product Name": product_name,
                    "Category": category,
                    "Price": price,
                    "Quantity": quantity,
                    "Supplier": supplier,
                    "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])

                st.session_state.inventory = pd.concat(
                    [st.session_state.inventory, new_row],
                    ignore_index=True
                )

                st.success("✅ Product added successfully")

# ---------------- UPDATE STOCK ----------------
elif menu == "Update Stock":

    st.subheader("🔄 Update Product Stock")

    if st.session_state.inventory.empty:
        st.warning("⚠ No products available")
    else:

        product = st.selectbox(
            "Select Product",
            st.session_state.inventory["Product Name"]
        )

        new_qty = st.number_input(
            "New Quantity",
            min_value=0,
            step=1
        )

        if st.button("Update Stock"):

            index = st.session_state.inventory[
                st.session_state.inventory["Product Name"] == product
            ].index[0]

            st.session_state.inventory.at[index, "Quantity"] = new_qty
            st.session_state.inventory.at[
                index,
                "Last Updated"
            ] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.success("✅ Stock updated successfully")

# ---------------- SEARCH PRODUCT ----------------
elif menu == "Search Product":

    st.subheader("🔍 Search Product")

    search = st.text_input("Enter Product Name")

    if st.button("Search"):

        result = st.session_state.inventory[
            st.session_state.inventory["Product Name"]
            .str.contains(search, case=False, na=False)
        ]

        if result.empty:
            st.warning("⚠ No matching product found")
        else:
            st.dataframe(result, use_container_width=True)

# ---------------- REMOVE PRODUCT ----------------
elif menu == "Remove Product":

    st.subheader("❌ Remove Product")

    if st.session_state.inventory.empty:
        st.warning("⚠ Inventory is empty")

    else:

        product = st.selectbox(
            "Select Product to Remove",
            st.session_state.inventory["Product Name"]
        )

        if st.button("Remove Product"):

            st.session_state.inventory = (
                st.session_state.inventory[
                    st.session_state.inventory["Product Name"] != product
                ]
            )

            st.success("✅ Product removed successfully")

# ---------------- INVENTORY REPORT ----------------
elif menu == "Inventory Report":

    st.subheader("📑 Inventory Report")

    if st.session_state.inventory.empty:
        st.info("ℹ No inventory data available")

    else:

        inventory = st.session_state.inventory.copy()

        inventory["Stock Value"] = (
            inventory["Price"] * inventory["Quantity"]
        )

        st.dataframe(
            inventory,
            use_container_width=True
        )

        csv = inventory.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Report",
            data=csv,
            file_name="inventory_report.csv",
            mime="text/csv"
        )

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":

    st.subheader("📈 Inventory Analytics")

    if st.session_state.inventory.empty:
        st.info("ℹ No data available for analytics")

    else:

        inventory = st.session_state.inventory.copy()

        inventory["Stock Value"] = (
            inventory["Price"] * inventory["Quantity"]
        )

        st.bar_chart(
            inventory.set_index("Product Name")["Quantity"]
        )

        st.bar_chart(
            inventory.set_index("Product Name")["Stock Value"]
        )

        low_stock_items = inventory[inventory["Quantity"] < 5]

        st.subheader("⚠ Low Stock Products")

        if low_stock_items.empty:
            st.success("✅ No low stock items")
        else:
            st.dataframe(low_stock_items)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© 2026 Smart Inventory Management System | Built with Streamlit")