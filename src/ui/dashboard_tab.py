from dash import html
import dash_bootstrap_components as dbc


def get_dashboard_tab():
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                html.H2("🧠 Welcome to DeepLens Dashboard", className="mb-4 text-center"),
                width=12
            )
        ]),

        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Activation Explorer", className="fw-bold"),
                    dbc.CardBody([
                        html.P(
                            "Explore intermediate activations of your model and understand feature representations.",
                            className="card-text"
                        ),
                        dbc.Button("Go to Activations", color="primary", href="/dashboard/activations")
                    ])
                ], className="mb-4 shadow-sm"),
                md=4
            ),

            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("XAI Visualizer", className="fw-bold"),
                    dbc.CardBody([
                        html.P(
                            "Use Grad-CAM, Integrated Gradients and other techniques to explain model behavior.",
                            className="card-text"
                        ),
                        dbc.Button("Go to XAI", color="info", href="/dashboard/xai")
                    ])
                ], className="mb-4 shadow-sm"),
                md=4
            ),

            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Evaluation Lab", className="fw-bold"),
                    dbc.CardBody([
                        html.P(
                            "Evaluate your model on test data and visualize performance metrics like accuracy and confusion matrix.",
                            className="card-text"
                        ),
                        dbc.Button("Go to Evaluation", color="success", href="/dashboard/evaluation")
                    ])
                ], className="mb-4 shadow-sm"),
                md=4
            )
        ])
    ], fluid=True)