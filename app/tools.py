import inspect
from app import services



# A dictionary of all the available tools
tools = {
    "fetch_all_tickets": services.fetch_and_store_tickets,
}

from pydantic import ValidationError
from sqlalchemy.orm import Session

# Function to call a tool by name
async def call_tool(db: Session, tool_name: str, tool_args: dict):
    """
    Calls a tool by name with the given arguments.
    """
    # Check if the tool exists
    if tool_name not in tools:
        return f"Tool {tool_name} not found."

    # Get the tool function
    tool_func = tools[tool_name]
    
    # Get the Pydantic model for the tool arguments
    sig = inspect.signature(tool_func)
    model_cls = None
    for param in sig.parameters.values():
        if param.name == "args":
            model_cls = param.annotation
            break

    try:
        # Validate the tool arguments
        if model_cls:
            if not tool_args:
                tool_args = {}
            validated_args = model_cls(**tool_args)
            # Call the tool function
            if inspect.iscoroutinefunction(tool_func):
                return await tool_func(db, args=validated_args)
            else:
                return tool_func(db, args=validated_args)
        else:
            # Call the tool function without arguments
            if inspect.iscoroutinefunction(tool_func):
                return await tool_func(db)
            else:
                return tool_func(db)

    except ValidationError as e:
        return f"Invalid arguments for tool {tool_name}: {e}"
    except Exception as e:
        return f"Error calling tool {tool_name}: {e}"