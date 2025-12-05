import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Ellipse, Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.gridspec import GridSpec
import streamlit.components.v1 as components

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Interactive Physics Lab",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UTILITY: RENDER MATPLOTLIB ANIMATION IN STREAMLIT ---
def render_animation(anim):
    """
    Converts a matplotlib animation to an interactive HTML component
    """
    with st.spinner("Rendering Simulation... (This may take a moment)"):
        js_html = anim.to_jshtml()
        components.html(js_html, height=700, scrolling=False)

# ==========================================
# 1. HOMEPAGE
# ==========================================
def show_home():
    st.title("🌌 Virtual Physics Laboratory")
    st.markdown("""
    Welcome to the Virtual Physics Lab. This platform uses Python to visualize complex 
    physical phenomena, from Quantum Mechanics to General Relativity.
    
    ### How to use:
    Use the **Sidebar (Left)** to navigate between different experiments.
    
    ### Available Experiments:
    1.  **Gravitational Lensing**: How massive objects warp spacetime and light.
    2.  **Michelson Interferometer**: Using light interference to measure microscopic distances.
    3.  **Coupled Pendulums**: Visualizing normal modes and beat frequencies.
    4.  **Young's Double Slit (Electrons)**: Wave-particle duality.
    5.  **Casimir Effect**: Vacuum fluctuations and quantum forces.
    6.  **Hawking Radiation**: Black hole evaporation via virtual particles.
    7.  **Vacuum Decay**: The catastrophe of the Higgs field tunneling.
    """)
    
    st.info("👈 Select an experiment from the sidebar to begin.")

# ==========================================
# 2. GRAVITATIONAL LENSING
# ==========================================
def show_lensing():
    st.header("🔭 Gravitational Lensing")
    st.markdown("**Concept:** Gravity bends light. A massive object (like a galaxy cluster) acts as a lens, distorting the image of stars behind it.")

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')
    ax.set_xlim(-10, 10)
    ax.set_ylim(-5, 5)

    # Objects
    earth = Circle((-8, 0), 0.3, color='deepskyblue', zorder=10)
    ax.add_patch(earth)
    ax.text(-8, -1.2, "Earth", color='deepskyblue', ha='center')

    lens_main = Ellipse((0, 0), 2.5, 1.5, color='gold', alpha=0.8, zorder=5)
    ax.add_patch(lens_main)
    ax.text(0, -2, "Galaxy Cluster", color='gold', ha='center')

    star = Circle((8, 0), 0.2, color='white', zorder=5)
    ax.add_patch(star)

    # Lines
    beam_top, = ax.plot([], [], color='white', linewidth=2, alpha=0.8)
    beam_bottom, = ax.plot([], [], color='white', linewidth=2, alpha=0.8)
    app_top, = ax.plot([], [], color='red', linestyle='--', alpha=0)
    app_bot, = ax.plot([], [], color='red', linestyle='--', alpha=0)
    img_top = Circle((-8, 0), 0.1, color='red', alpha=0)
    img_bot = Circle((-8, 0), 0.1, color='red', alpha=0)
    ax.add_patch(img_top)
    ax.add_patch(img_bot)
    
    txt = ax.text(-8, 3.5, "", color='red', ha='center')

    def get_path(t, sign):
        x = 8 * (1 - 2*t)
        y = sign * 2.5 * np.sin(t * np.pi)
        return x, y

    def animate(frame):
        if frame <= 50:
            t = frame / 50.0
            tp = np.linspace(0, t, frame+1)
            beam_top.set_data(*get_path(tp, 1))
            beam_bottom.set_data(*get_path(tp, -1))
        else:
            # Dashed lines
            prog = min(1, (frame-50)/30.0)
            dash_x = np.linspace(-8, -8 + 16*prog, 10)
            dash_y_top = np.linspace(0, 5*prog, 10)
            dash_y_bot = np.linspace(0, -5*prog, 10)
            app_top.set_data(dash_x, dash_y_top)
            app_bot.set_data(dash_x, dash_y_bot)
            app_top.set_alpha(0.5)
            app_bot.set_alpha(0.5)
            
            if prog > 0.1:
                img_top.center = (-8+16*prog, 5*prog)
                img_bot.center = (-8+16*prog, -5*prog)
                img_top.set_alpha(1)
                img_bot.set_alpha(1)
                txt.set_text("Apparent Position\n(Einstein Ring)")
                
        return beam_top, beam_bottom, app_top, app_bot, img_top, img_bot, txt

    ani = animation.FuncAnimation(fig, animate, frames=100, interval=40, blit=True)
    render_animation(ani)

# ==========================================
# 3. MICHELSON INTERFEROMETER
# ==========================================
def show_interferometer():
    st.header("📏 Michelson Interferometer")
    st.markdown("**Concept:** Splitting a light beam and recombining it creates interference patterns. Moving a mirror by a tiny fraction of a wavelength shifts the pattern.")

    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12, 6))
    ax_diag = fig.add_subplot(1, 2, 1)
    ax_view = fig.add_subplot(1, 2, 2)
    
    # Diagram Setup
    ax_diag.axis('off'); ax_diag.set_xlim(-6, 6); ax_diag.set_ylim(-6, 6)
    splitter = Rectangle((-0.1, -1.5), 0.2, 3, angle=45, color='cyan', alpha=0.5)
    ax_diag.add_patch(splitter)
    ax_diag.add_patch(Rectangle((-1.5, 4.8), 3, 0.4, color='silver')) # Fixed
    
    mirror_move = Rectangle((4.8, -1.5), 0.4, 3, color='silver')
    ax_diag.add_patch(mirror_move)
    
    beams = [ax_diag.plot([], [], color='red', linewidth=3, alpha=0.8)[0] for _ in range(6)]
    
    # View Setup
    ax_view.axis('off'); ax_view.set_title("Detector View")
    x = np.linspace(-10, 10, 100)
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)
    img = ax_view.imshow(np.zeros_like(R), cmap='hot', vmin=0, vmax=1)

    def animate(frame):
        # Mirror Logic
        mx = 4.8 + 0.8 * np.sin(frame * 0.1)
        mirror_move.set_x(mx)
        
        # Beam Logic (Simplified for web performance)
        beams[0].set_data([-5, 0], [0, 0]) # Source
        beams[1].set_data([0, 0], [0, 4.8]) # Up
        beams[2].set_data([0, mx], [0, 0]) # Right
        beams[3].set_data([0, 0], [4.8, 0]) # Ret Up
        beams[4].set_data([mx, 0], [0, 0]) # Ret Right
        beams[5].set_data([0, 0], [0, -5]) # To Detector
        
        # Interference Logic
        delta_L = 2 * (mx - 4.8)
        Z = np.cos(0.5 * R**2 + 2*np.pi*delta_L)**2
        img.set_data(Z)
        return beams + [mirror_move, img]

    ani = animation.FuncAnimation(fig, animate, frames=100, interval=50, blit=True)
    render_animation(ani)

# ==========================================
# 4. COUPLED PENDULUMS
# ==========================================
def show_pendulum():
    st.header("⏰ Coupled Pendulums")
    st.markdown("**Concept:** Energy transfer between two oscillators connected by a spring creates 'beats'.")
    
    plt.style.use('dark_background')
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    titles = ["In-Phase", "Out-of-Phase", "Beats (Superposition)"]
    lines_rods = []
    bobs = []
    springs = []
    
    for i, ax in enumerate(axes):
        ax.set_title(titles[i], color='white', fontsize=10)
        ax.set_xlim(-1, 1); ax.set_ylim(-1.2, 0.2); ax.axis('off')
        ax.plot([-0.6, 0.6], [0, 0], color='gray')
        
        r1, = ax.plot([], [], 'w-')
        r2, = ax.plot([], [], 'w-')
        b1 = Circle((0,0), 0.08, color='cyan')
        b2 = Circle((0,0), 0.08, color='magenta')
        spr, = ax.plot([], [], 'y-')
        
        ax.add_patch(b1); ax.add_patch(b2)
        lines_rods.append((r1, r2))
        bobs.append((b1, b2))
        springs.append(spr)

    t = np.linspace(0, 20, 200)
    w1, w2 = 3.0, 3.5
    
    def animate(i):
        # 1. In Phase
        th1 = 0.2 * np.cos(w1 * t[i])
        th2 = 0.2 * np.cos(w1 * t[i])
        coords1 = (th1, th2)
        
        # 2. Out Phase
        th3 = 0.2 * np.cos(w2 * t[i])
        th4 = -0.2 * np.cos(w2 * t[i])
        coords2 = (th3, th4)
        
        # 3. Beats
        th5 = 0.1 * np.cos(w1 * t[i]) + 0.1 * np.cos(w2 * t[i])
        th6 = 0.1 * np.cos(w1 * t[i]) - 0.1 * np.cos(w2 * t[i])
        coords3 = (th5, th6)
        
        all_coords = [coords1, coords2, coords3]
        
        artists = []
        for j in range(3):
            a, b = all_coords[j]
            x1, y1 = -0.4 + np.sin(a), -np.cos(a)
            x2, y2 = 0.4 + np.sin(b), -np.cos(b)
            
            lines_rods[j][0].set_data([-0.4, x1], [0, y1])
            lines_rods[j][1].set_data([0.4, x2], [0, y2])
            bobs[j][0].center = (x1, y1)
            bobs[j][1].center = (x2, y2)
            springs[j].set_data([x1, x2], [y1, y2])
            
            artists.extend([lines_rods[j][0], lines_rods[j][1], bobs[j][0], bobs[j][1], springs[j]])
            
        return artists

    ani = animation.FuncAnimation(fig, animate, frames=200, interval=30, blit=True)
    render_animation(ani)

# ==========================================
# 5. DOUBLE SLIT
# ==========================================
def show_doubleslit():
    st.header("🌊 Young's Double Slit (Electrons)")
    st.markdown("**Concept:** Electrons arrive as particles (discrete dots), but their probability distribution forms a wave interference pattern.")

    plt.style.use('dark_background')
    fig = plt.figure(figsize=(10, 6))
    gs = GridSpec(2, 2)
    
    ax_top = fig.add_subplot(gs[0, :])
    ax_top.set_title("Top-Down View"); ax_top.axis('off')
    ax_top.set_xlim(-2, 3); ax_top.set_ylim(-1.5, 1.5)
    ax_top.plot([0,0], [1.5, 0.2], 'gray', lw=3)
    ax_top.plot([0,0], [-0.2, 0.2], 'gray', lw=3)
    ax_top.plot([0,0], [-1.5, -0.2], 'gray', lw=3)
    ax_top.plot([2.5, 2.5], [-1.5, 1.5], 'cyan', alpha=0.5)
    dot, = ax_top.plot([], [], 'o', color='lime')
    
    ax_bot = fig.add_subplot(gs[1, 0])
    ax_bot.set_title("Detector View"); ax_bot.set_facecolor('black')
    ax_bot.set_xlim(-0.5, 0.5); ax_bot.set_ylim(-1, 1); ax_bot.axis('off')
    impacts, = ax_bot.plot([], [], 'o', color='lime', ms=2, alpha=0.6)
    
    ax_graph = fig.add_subplot(gs[1, 1])
    ax_graph.set_title("Accumulation vs Theory")
    ax_graph.set_yticks([])
    ax_graph.set_ylim(-1, 1); ax_graph.invert_xaxis()
    
    y = np.linspace(-1, 1, 100)
    # Approx pattern
    I = np.cos(10*y)**2 * np.sinc(2*y)**2
    ax_graph.plot(I, y, 'y-', alpha=0.5)
    
    bins = np.linspace(-1, 1, 30)
    bars = ax_graph.barh(bins[:-1], np.zeros(29), height=np.diff(bins), color='cyan', alpha=0.6)
    
    landed_y = []

    def animate(frame):
        # Determine target
        if frame % 5 == 0:
            # Rejection sampling for target
            while True:
                r_y = np.random.uniform(-1, 1)
                prob = (np.cos(10*r_y)**2 * np.sinc(2*r_y)**2)
                if np.random.random() < prob:
                    landed_y.append(r_y)
                    break
        
        # Flight animation (simplified)
        sub = frame % 5
        prog = sub / 5.0
        # Check if we have a target
        if landed_y:
            target = landed_y[-1]
            dot.set_data([-1.5 + 4*prog], [target * prog])
        
        # Impacts
        impacts.set_data(np.random.normal(0, 0.1, len(landed_y)), landed_y)
        
        # Histogram
        hist, _ = np.histogram(landed_y, bins=bins)
        if len(landed_y) > 0:
            hist = hist / max(hist) if max(hist) > 0 else hist
            for bar, h in zip(bars, hist):
                bar.set_width(h)
                
        return [dot, impacts] + list(bars)

    ani = animation.FuncAnimation(fig, animate, frames=100, interval=20, blit=False)
    render_animation(ani)

# ==========================================
# 6. CASIMIR EFFECT
# ==========================================
def show_casimir():
    st.header("👻 The Casimir Effect")
    st.markdown("**Concept:** Vacuum fluctuations are suppressed between two plates. The higher pressure of 'virtual particles' outside pushes the plates together.")

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off'); ax.set_xlim(-4, 4); ax.set_ylim(-3, 3)
    
    plate_L = Rectangle((-2.1, -2), 0.2, 4, color='silver')
    plate_R = Rectangle((1.9, -2), 0.2, 4, color='silver')
    ax.add_patch(plate_L); ax.add_patch(plate_R)
    
    lines_out = [ax.plot([], [], 'c-', alpha=0.2)[0] for _ in range(20)]
    lines_in = [ax.plot([], [], 'm-', alpha=0.6)[0] for _ in range(5)]
    
    arr_L = FancyArrowPatch((-3, 0), (-2.2, 0), mutation_scale=20, color='red')
    arr_R = FancyArrowPatch((3, 0), (2.2, 0), mutation_scale=20, color='red')
    ax.add_patch(arr_L); ax.add_patch(arr_R)

    def animate(frame):
        d = 2.0 * (1 - frame/100.0) + 0.5
        plate_R.set_x(d)
        
        # Arrows grow
        arr_L.set_positions((-2-d*0.5, 0), (-2.1, 0))
        arr_R.set_positions((d+0.2+d*0.5, 0), (d+0.2, 0))
        
        x_in = np.linspace(-2, d, 50)
        for i, line in enumerate(lines_in):
            y = 0.5 * np.sin((i+1)*np.pi * (x_in + 2)/(d+2)) * np.cos(frame*0.2)
            line.set_data(x_in, y)
            
        return [plate_R, arr_L, arr_R] + lines_in

    ani = animation.FuncAnimation(fig, animate, frames=80, interval=40, blit=True)
    render_animation(ani)

# ==========================================
# 7. HAWKING RADIATION
# ==========================================
def show_hawking():
    st.header("🕳️ Hawking Radiation")
    st.markdown("**Concept:** Virtual particle pairs form near the event horizon. One falls in (negative energy), one escapes (radiation). The black hole loses mass.")

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis('off'); ax.set_xlim(-3, 3); ax.set_ylim(-3, 3)
    
    bh = Circle((0,0), 1, color='black', zorder=5)
    ax.add_patch(bh)
    ax.add_patch(Circle((0,0), 1, color='white', fill=False, linestyle='--'))
    
    # Particles
    p1, = ax.plot([], [], 'co', ms=5) # Escape
    p2, = ax.plot([], [], 'ro', ms=5) # Fall
    
    def animate(frame):
        cycle = frame % 40
        if cycle < 10: # Spawning
            p1.set_data([1.1], [0])
            p2.set_data([0.9], [0])
            p1.set_alpha(cycle/10)
            p2.set_alpha(cycle/10)
        else:
            # Moving
            t = (cycle - 10) / 30.0
            p1.set_data([1.1 + t*1.5], [t*0.5]) # Fly away
            p2.set_data([0.9 - t*0.9], [0]) # Fall in
            p2.set_alpha(1 - t) # Fade
            
        return p1, p2

    ani = animation.FuncAnimation(fig, animate, frames=120, interval=30, blit=True)
    render_animation(ani)

# ==========================================
# 8. VACUUM DECAY
# ==========================================
def show_vacuum():
    st.header("💥 Vacuum Decay")
    st.markdown("**Concept:** If the Higgs field is in a 'false vacuum', it can tunnel through an energy barrier. This creates a bubble of 'new physics' that expands at light speed.")
    
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Graph
    ax1.set_ylim(-2, 4); ax1.set_xlim(-1, 3.5); ax1.axis('off')
    x = np.linspace(-1, 3.5, 100)
    y = 0.5*x**4 - 2.66*x**3 + 4*x**2
    ax1.plot(x, y, 'w')
    ball, = ax1.plot([], [], 'co', ms=10)
    
    # Space
    ax2.axis('off'); ax2.set_xlim(-10, 10); ax2.set_ylim(-10, 10)
    stars = ax2.scatter(np.random.uniform(-10,10,100), np.random.uniform(-10,10,100), c='w', s=5)
    bubble = Circle((0,0), 0, color='magenta', alpha=0.5)
    ax2.add_patch(bubble)
    
    def animate(frame):
        # 1. Tunneling
        if frame < 30:
            ball.set_data([0], [0]) # False vacuum
        elif frame < 50:
            ball.set_data([2.5 * (frame-30)/20.0], [1.5]) # Tunneling
            ball.set_color('yellow')
        else:
            ball.set_data([2.7], [-1]) # True vacuum
            ball.set_color('magenta')
            
        # 2. Bubble
        if frame > 50:
            r = (frame - 50) * 0.3
            bubble.set_radius(r)
            
        return ball, bubble

    ani = animation.FuncAnimation(fig, animate, frames=100, interval=40, blit=True)
    render_animation(ani)

# ==========================================
# NAVIGATION LOGIC
# ==========================================

# Sidebar Menu
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to:", 
    ["Home", 
     "Gravitational Lensing", 
     "Michelson Interferometer", 
     "Coupled Pendulums",
     "Double Slit (Electrons)",
     "Casimir Effect",
     "Hawking Radiation",
     "Vacuum Decay"]
)

# Routing
if selection == "Home":
    show_home()
elif selection == "Gravitational Lensing":
    show_lensing()
elif selection == "Michelson Interferometer":
    show_interferometer()
elif selection == "Coupled Pendulums":
    show_pendulum()
elif selection == "Double Slit (Electrons)":
    show_doubleslit()
elif selection == "Casimir Effect":
    show_casimir()
elif selection == "Hawking Radiation":
    show_hawking()
elif selection == "Vacuum Decay":
    show_vacuum()

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Created with Python & Streamlit")