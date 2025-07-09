import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sympy as sp
from io import BytesIO
from PIL import Image
import base64
import matplotlib.pyplot as plt

#page setup
st.set_page_config(
    page_title="Graph Plotter",
    layout="centered"
)
st.title("📊 2D / 3D Graph Plotter")

#----user input----
st.markdown("Enter a mathematical function using 'x' for 2D or 'x' and 'y' for 3D.")
func_input = st.text_input("🔢 Enter Function:", placeholder="sin(x)")
plot_type = st.radio("📐 Plot Type:", ["2D", "3D"])

#custom axis range
st.markdown("Set custom axis range (optional):")
x_min = st.number_input("X min", value=-5.0)
x_max = st.number_input("X max", value=5.0)

if plot_type == "3D":
    y_min = st.number_input("Y min", value=-5.0)
    y_max = st.number_input("Y max", value=5.0)
else:
    y_min = None
    y_max = None

#derivative or integral option
if plot_type == "2D":
    st.subheader("Derivative or Integral")
    show_derivative = st.checkbox("Show Derivative")
    show_integral = st.checkbox("Show Indefinite Integral")
else:
    show_derivative = False
    show_integral = False

#function parsing
x, y = sp.symbols('x y')
try:
    func_expr = sp.sympify(func_input)
except (sp.SympifyError, TypeError):
    st.error("Invalid function input. Please enter a valid mathematical expression.")
    st.stop()

def safe_filename(s):
    return "".join(c for c in s if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()

#plotting
if plot_type == "2D":
    x_vals = np.linspace(x_min, x_max, 800)
    f_lambdified = sp.lambdify(x, func_expr, modules=["numpy"])
    try:
        y_vals = f_lambdified(x_vals)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name="f(X)"))

        #derivative
        if show_derivative:
            derivative_expr = sp.diff(func_expr, x)
            derivative_lambdified = sp.lambdify(x, derivative_expr, modules=["numpy"])
            y_derivative_vals = derivative_lambdified(x_vals)
            fig.add_trace(go.Scatter(x=x_vals, y=y_derivative_vals, mode='lines', name="f'(X)"))

        #integral
        if show_integral:
            integral_expr = sp.integrate(func_expr, x)
            integral_lambdified = sp.lambdify(x, integral_expr, modules=["numpy"])
            y_integral_vals = integral_lambdified(x_vals)
            fig.add_trace(go.Scatter(x=x_vals, y=y_integral_vals, mode='lines', name="∫f(X) dX"))

        fig.update_layout(
            title = f"2D plot of {func_input}",
            xaxis_title="X-axis",
            yaxis_title="Y-axis",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Matplotlib static PNG export
        plt.figure(figsize=(7, 4))
        plt.plot(x_vals, y_vals, label="f(X)")
        if show_derivative:
            plt.plot(x_vals, y_derivative_vals, label="f'(X)")
        if show_integral:
            plt.plot(x_vals, y_integral_vals, label="∫f(X) dX")
        plt.title(f"2D plot of {func_input}")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.legend()
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        img_bytes = buf.read()
        img_base64 = base64.b64encode(img_bytes).decode()
        filename = safe_filename(func_input) or "plot"
        st.markdown(
            f'<a href="data:image/png;base64,{img_base64}" download="{filename}.png">📥 Download Plot as PNG</a>',
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Error in plotting: {e}")

else:
    x_vals = np.linspace(x_min, x_max, 200)
    y_vals = np.linspace(y_min, y_max, 200)
    X, Y = np.meshgrid(x_vals, y_vals)
    try:
        f_lambdified_3d = sp.lambdify((x, y), func_expr, modules=["numpy"])
        Z = f_lambdified_3d(X, Y)
        fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
        fig.update_layout(
            title=f"3D Surface Plot of {func_input}",
            scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="f(x, y)"),
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info("PNG download for 3D plot is not available without Kaleido. You may use screenshot tools or download the interactive HTML plot below.")

        # Interactive HTML download
        fig_html = fig.to_html(include_plotlyjs='cdn')
        html_bytes = fig_html.encode()
        html_b64 = base64.b64encode(html_bytes).decode()
        filename = safe_filename(func_input) or "plot3d"
        st.markdown(
            f'<a href="data:text/html;base64,{html_b64}" download="{filename}.html">📥 Download Plot as HTML</a>',
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Error in plotting: {e}")

# Add a footer
st.markdown("---")
st.markdown("Made with ❤️ by [Anurag Panda](https://linkedin.com/in/anurag-panda-)")
