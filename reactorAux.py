### auxiliary functions to support reactor

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from settings import DEFAULT_FUEL_ENRICHMENT


def pack_widgets(reactor):
    reactor.canvas.grid(row=0, column=0, columnspan=3)
    reactor.plot_frame.grid(row=0, column=4, rowspan=9)
    reactor.figcanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    reactor.run_button.grid(row=1, column=1)
    reactor.pause_button.grid(row=2, column=1)
    reactor.reset_button.grid(row=3, column=1)
    reactor.toggle_source_button.grid(row=4, column=1)
    reactor.emit_neutron_button.grid(row=5, column=1)
    reactor.time_step_slider_label.grid(row=6, column=0)
    reactor.time_step_slider.grid(row=6, column=1)
    reactor.time_step_display_label.grid(row=6, column=2)
    reactor.enrichment_entry_label.grid(row=7, column=0)
    reactor.enrichment_entry.grid(row=7, column=1)
    reactor.enrichment_button.grid(row=7, column=2)
    reactor.toggle_controlrod_button.grid(row=8, column=1)


def initialize_controls(reactor, root):
    """Builds all the buttons, sliders, and labels used to control the reactor"""
    reactor.run_button = tk.Button(root, text="Run", command=reactor.run_reactor)
    reactor.pause_button = tk.Button(root, text="Pause", command=reactor.pause_reactor)
    reactor.reset_button = tk.Button(root, text="Reset", command=reactor.reset_reactor)
    reactor.toggle_source_button = tk.Button(
        root, text="Toggle neutron source", command=reactor.toggle_source
    )
    reactor.emit_neutron_button = tk.Button(
        root, text="Emit neutron", command=reactor.emit_neutron
    )

    reactor.time_step_slider_label = tk.Label(root, text="Time step: ")
    reactor.time_step_slider = tk.Scale(
        root,
        from_=0,
        to=99,
        orient="horizontal",
        showvalue=0,
        command=reactor.on_slider_move,
    )
    reactor.time_step_slider.set(33)
    reactor.time_step = 1e-8 * 10 ** (reactor.time_step_slider.get() / 33)
    reactor.time_step_display_label = tk.Label(root, text=str(reactor.time_step))

    reactor.enrichment_entry_label = tk.Label(root, text="Enrichment (%): ")
    reactor.enrichment_entry_var = tk.DoubleVar(root, value=DEFAULT_FUEL_ENRICHMENT)
    reactor.enrichment_entry = tk.Entry(root, textvariable=reactor.enrichment_entry_var)
    reactor.enrichment_button = tk.Button(
        root, text="Change enrichment", command=reactor.change_enrichment
    )
    reactor.toggle_controlrod_button = tk.Button(
        root, text="Toggle Control Rods", command=reactor.toggle_controlrod
    )


def update_graphs(reactor):
    """Updates time, neutron count, and neutron energy data, then updates the graphs accordingly"""
    reactor.time_data.append(reactor.time_elapsed)
    reactor.neutron_count_data.append(reactor.neutron_count)
    reactor.neutron_energy_data.append(reactor.average_neutron_energy)
    reactor.ax1.clear()
    reactor.ax1.plot(reactor.time_data, reactor.neutron_count_data, color="steelblue")
    reactor.ax1.set_xlim(left=0)
    reactor.ax1.set_ylim(bottom=0)
    reactor.ax1.set_ylabel("Neutron Count")
    reactor.ax1.tick_params(axis="x", length=0, direction="in", labelbottom=False)
    reactor.ax1.grid()
    reactor.ax2.clear()
    reactor.ax2.plot(reactor.time_data, reactor.neutron_energy_data)
    reactor.ax2.set_xlim(left=0)
    reactor.ax2.set_ylim(bottom=0)
    reactor.ax2.set_ylabel("Average neutron energy")
    reactor.ax2.set_xlabel("Time (s)")
    reactor.ax2.tick_params(axis="x", labelrotation=45)
    reactor.ax2.grid()
    reactor.figcanvas.draw_idle()


def initialize_graphs(reactor):
    """Builds the graphs beside the reactor, calls update_plot at the end to begin updating loop"""
    reactor.fig = Figure(figsize=(5, 6), dpi=100)
    # Axis for neutron count
    reactor.fig.tight_layout()
    reactor.ax1 = reactor.fig.add_subplot(211)
    # Axis for neutron energy
    reactor.ax2 = reactor.fig.add_subplot(212)
    reactor.figcanvas = FigureCanvasTkAgg(reactor.fig, master=reactor.plot_frame)
    reactor.time_data, reactor.neutron_count_data, reactor.neutron_energy_data = (
        [],
        [],
        [],
    )
