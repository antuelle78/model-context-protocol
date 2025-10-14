import inspect
import json
from sqlalchemy.orm import Session

from app import services
from app.schemas import (
    GetReportOpenByPriorityArgs,
    GetReportByAssignmentGroupArgs,
    CreateNewTicketServiceNowArgs,
    GetGlpiFullAssetDumpArgs,
    TicketCreateRequest,
)

def get_tool_definitions():
    """Generate a list of tool definitions for all available tools."""
    tool_definitions = []

    # ServiceNow Tools
    servicenow_tools = {
        "fetch_all_servicenow_tickets": services.fetch_and_store_tickets,
        "get_report_open_by_priority": services.get_tickets_by_priority,
        "get_report_by_assignment_group": services.get_tickets_by_assignment_group,
        "get_report_recently_resolved": services.get_recently_resolved_tickets,
        "create_new_ticket": services.create_ticket,
    }
    for tool_name, tool_func in servicenow_tools.items():
        sig = inspect.signature(tool_func)
        input_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        for param in sig.parameters.values():
            if param.name not in ["db", "args"]:
                input_schema["properties"][param.name] = {"type": "string"}
                if param.default == inspect.Parameter.empty:
                    input_schema["required"].append(param.name)
        
        tool_definitions.append({
            "name": tool_name,
            "title": tool_name.replace("_", " ").title(),
            "description": tool_func.__doc__.strip() if tool_func.__doc__ else "",
            "inputSchema": input_schema,
            "outputSchema": {"type": "object", "properties": {"data": {"type": "object"}}},
            "annotations": {},
        })

    # GLPI Tools
    glpi_tools = {
        "get_glpi_laptop_count": services.glpi_service.get_asset_count,
        "get_glpi_pc_count": services.glpi_service.get_asset_count,
        "get_glpi_monitor_count": services.glpi_service.get_asset_count,
        "get_glpi_os_distribution": services.glpi_service.get_assets,
        "get_glpi_full_asset_dump": services.glpi_service.get_full_asset_dump,
        "fetch_all_glpi_inventory": services.glpi_service.fetch_and_store_inventory,
    }
    for tool_name, tool_func in glpi_tools.items():
        sig = inspect.signature(tool_func)
        input_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        for param in sig.parameters.values():
            if param.name not in ["self", "itemtype", "query_params"]:
                input_schema["properties"][param.name] = {"type": "string"}
                if param.default == inspect.Parameter.empty:
                    input_schema["required"].append(param.name)
        
        tool_definitions.append({
            "name": tool_name,
            "title": tool_name.replace("_", " ").title(),
            "description": tool_func.__doc__.strip() if tool_func.__doc__ else "",
            "inputSchema": input_schema,
            "outputSchema": {"type": "object", "properties": {"data": {"type": "object"}}},
            "annotations": {},
        })

    # File Tools
    file_tools = {
        "file_fetcher": services.read_directory,
    }
    for tool_name, tool_func in file_tools.items():
        sig = inspect.signature(tool_func)
        input_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        for param in sig.parameters.values():
            input_schema["properties"][param.name] = {"type": "string"}
            if param.default == inspect.Parameter.empty:
                input_schema["required"].append(param.name)

        tool_definitions.append({
            "name": tool_name,
            "title": tool_name.replace("_", " ").title(),
            "description": tool_func.__doc__.strip() if tool_func.__doc__ else "",
            "inputSchema": input_schema,
            "outputSchema": {"type": "object", "properties": {"data": {"type": "object"}}},
            "annotations": {},
        })

    return tool_definitions


async def execute_tool(db: Session, tool_name: str, tool_args: dict):
    """Executes a tool by calling the corresponding service function."""
    print(f"Executing tool: {tool_name} with args: {tool_args}")
    try:
        # GLPI tools
        if tool_name.startswith("get_glpi") or tool_name == "fetch_all_glpi_inventory":
            glpi_tools = {
                "get_glpi_laptop_count": (services.glpi_service.get_asset_count, {"itemtype": "Computer", "query_params": {"criteria[0][field]": "type", "criteria[0][searchtype]": "contains", "criteria[0][value]": "laptop"}}),
                "get_glpi_pc_count": (services.glpi_service.get_asset_count, {"itemtype": "Computer", "query_params": {"criteria[0][field]": "type", "criteria[0][searchtype]": "contains", "criteria[0][value]": "desktop"}}),
                "get_glpi_monitor_count": (services.glpi_service.get_asset_count, {"itemtype": "Monitor"}),
                "get_glpi_os_distribution": (services.glpi_service.get_assets, {"itemtype": "Computer", "query_params": {"expand_dropdowns": True, "with_operatingsystems": True}}),
                "get_glpi_full_asset_dump": (services.glpi_service.get_full_asset_dump, tool_args),
                "fetch_all_glpi_inventory": (services.glpi_service.fetch_and_store_inventory, {}),
            }
            if tool_name in glpi_tools:
                tool_func, kwargs = glpi_tools[tool_name]
                # Unpack Pydantic models
                for key, value in kwargs.items():
                    if hasattr(value, 'model_dump'):
                        kwargs[key] = value.model_dump()
                return tool_func(**kwargs)
        
        # ServiceNow tools
        elif tool_name.startswith("fetch_all") or tool_name.startswith("get_report") or tool_name.startswith("create"):
            servicenow_tools = {
                "fetch_all_servicenow_tickets": services.fetch_and_store_tickets,
                "get_report_open_by_priority": services.get_tickets_by_priority,
                "get_report_by_assignment_group": services.get_tickets_by_assignment_group,
                "get_report_recently_resolved": services.get_recently_resolved_tickets,
                "create_new_ticket": services.create_ticket,
            }
            if tool_name in servicenow_tools:
                tool_func = servicenow_tools[tool_name]
                # Pass db session if the function expects it
                sig = inspect.signature(tool_func)
                if "db" in sig.parameters:
                    tool_args["db"] = db
                
                # Unpack Pydantic models
                if tool_name == "get_report_open_by_priority":
                    tool_args = {"priority": tool_args["priority"], "db": db}
                elif tool_name == "get_report_by_assignment_group":
                    tool_args = {"group": tool_args["group"], "db": db}
                elif tool_name == "create_new_ticket":
                    tool_args = {"ticket_data": TicketCreateRequest(**tool_args), "db": db}
                else:
                    for key, value in tool_args.items():
                        if hasattr(value, 'model_dump'):
                            tool_args[key] = value.model_dump()

                if inspect.iscoroutinefunction(tool_func):
                    return await tool_func(**tool_args)
                else:
                    return tool_func(**tool_args)

        # File tools
        elif tool_name == "file_fetcher":
            return services.read_directory(**tool_args)

        return f"Tool {tool_name} not found."

    except Exception as e:
        import traceback
        print(f"Error executing tool '{tool_name}': {e}")
        traceback.print_exc()
        return f"An error occurred while executing the tool: {e}"
