from pathlib import Path
from ipydatagrid import DataGrid
import pandas as pd
from shared import INPUTS
from shiny import App, Inputs, Outputs, Session, reactive, ui, render
from shiny_validate import InputValidator, check
from shinywidgets import output_widget, register_widget

app_dir = Path(__file__).parent

app_ui = ui.page_fluid(
    ui.include_css(app_dir / "styles.css"),
    ui.panel_title("Movie survey"),
    # ui.card(
    #     ui.card_header("Demographics"),
    #     INPUTS["name"],
    #     INPUTS["country"],
    #     INPUTS["age"],
    # ),
    # ui.card(
    #     ui.card_header("Income"),
    #     INPUTS["income"],
    # ),
    # ui.card(
    #     ui.card_header("Ratings"),
    #     INPUTS["avengers"],
    #     INPUTS["spotlight"],
    #     INPUTS["the_big_short"],
    # ),

    ui.card(
            output_widget("table"),
            # ui.card_header("Penguin data"),
            # ui.output_data_frame("summary_statistics"),
            full_screen=True,
        ),
    ui.div(
        ui.input_action_button("submit", "Submit", class_="btn btn-primary"),
        class_="d-flex justify-content-end",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    input_validator = InputValidator()
    input_validator.add_rule("name", check.required())
    input_validator.add_rule("country", check.required())
    input_validator.add_rule("age", check.required())
    input_validator.add_rule("income", check.required())

    @reactive.effect
    @reactive.event(input.submit)
    def save_to_csv():
        input_validator.enable()
        if not input_validator.is_valid():
            return

        df = pd.DataFrame([{k: input[k]() for k in INPUTS.keys()}])

        responses = app_dir / "responses.csv"
        if not responses.exists():
            df.to_csv(responses, mode="a", header=True)
        else:
            df.to_csv(responses, mode="a", header=False)

        ui.modal_show(ui.modal("Form submitted, thank you!"))

    def read_responses():
        return pd.read_csv(app_dir / "responses.csv")

    def view_responses():
        return read_responses()

    tbl = DataGrid(read_responses()[[
        "name", "country", "age", "income","avengers","spotlight","the_big_short"]],
        editable=True, auto_fit_columns=True, index_name="index")
    register_widget("table", tbl)

    # Create a reactive value for tracking cell changes
    cell_changes = reactive.Value()

    cell_selection = reactive.Value()

    def on_cell_changed(cell):
        cell_changes.set(str(cell))

    def on_cell_selected(cell):
        cell_selection.set(str(cell))

    # register callback
    tbl.on_cell_change(on_cell_changed)

    # Print change, just to demonstrate
    @reactive.Effect
    def print_change():
        print(eval(cell_changes()))

    @reactive.Effect
    def print_selection():
        print(eval(cell_selection()))

    @reactive.Effect
    def save_cell_changes():
        # Save changes to csv
        df = read_responses()
        cell = eval(cell_changes())
        df.loc[cell["row"], cell["column"]] = cell["value"]
        clean_df = df
        # df.drop(columns=["Unnamed: 0"], inplace=True)
        clean_df.to_csv(app_dir / "responses.csv", mode="w", header=True, index=False)

    # @render.data_frame
    # def summary_statistics():
    #     return render.DataGrid(read_responses(), filters=True)


app = App(app_ui, server)
