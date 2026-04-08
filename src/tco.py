def calc_tco(app: dict) -> float:
    """
    Calculate Total Cost of Ownership (€/year) for one application.

    app must have: dev_resources, dev_cost_per_resource, support_resources,
    support_cost_per_resource, license_cost, infra_cost, hardware_sw_cost
    """
    annual_dev = app["dev_resources"] * app["dev_cost_per_resource"]
    annual_support = app["support_resources"] * app["support_cost_per_resource"]
    return (
        annual_dev
        + annual_support
        + app["license_cost"]
        + app["infra_cost"]
        + app["hardware_sw_cost"]
    )
