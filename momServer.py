#!/usr/bin/env python3
"""
MoM MCP Server
Exposes: generate_mom, send_mom
"""
import argparse
import json
import os
from fastmcp import FastMCP
from llama_index.llms.groq import Groq
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient



class MoMServer:
    def __init__(self):
        try:
            # Initialize Groq LLM
            self.llm = Groq(
                model="llama-3.1-8b-instant",
                api_key="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",
                request_timeout=120.0,
            )
            Settings.llm = self.llm


        except Exception as e:
            print(f"[ERROR] Failed to initialize MoMServer: {e}")
            raise

    def generate_mom(self, transcript: str) -> str:
        """Convert transcript to structured MoM."""
        try:
            prompt = f"""
            Convert the following meeting transcript into structured Minutes of Meeting (MoM).
            Include: Agenda, Key Points, Decisions, Action Items (with owners).

            Transcript:
            {transcript}
            """
            response = self.llm.complete(prompt)
            return response.text
        except Exception as e:
            print(f"[ERROR] generate_mom failed: {e}")
            raise


# ---- MCP Server ----
mom_server = MoMServer()
server = FastMCP("MoMMCP")

@server.tool(description="Generate Minutes of Meeting (MoM) from transcript")
def generate_mom(transcript: str) -> str:
    return mom_server.generate_mom(transcript)

@server.tool(description="Generate MoM from transcript and send it to participants via email")
async def send_mom(names: str, transcript: str) -> str:
    """Generate MoM from transcript and send it to participants via email.
    
    This tool handles the complete workflow:
    1. Generates the MoM from the transcript
    2. Sends the generated MoM via email
    
    Args:
        names: Comma-separated list of participant names (e.g., "Arun, Arvind")
        transcript: Meeting transcript to convert into MoM
    """
    try:
        # Step 1: Parse names and resolve emails
        name_list = [name.strip() for name in names.split(",") if name.strip()]
        
        # Step 2: Generate MoM
        print("📌 Step 1: Generating MoM from transcript...")
        mom = mom_server.generate_mom(transcript)
        print("✅ MoM generated successfully.")
        
        # Step 3: Send email with the generated MoM
        print("📌 Step 2: Sending email with generated MoM...")
        # Import here to avoid circular imports
        from llama_index.tools.mcp import BasicMCPClient
        
        # Create Gmail client
        gmail_client = BasicMCPClient("http://127.0.0.1:8000/sse")
        
        # Send email with the generated MoM content
        response = await gmail_client.call_tool("send_email", {
            "to": name_list,
            "subject": "Minutes of Meeting (MoM)",
            "body": mom,
        })
        
        print("✅ Email sent successfully.")
        
        # Extract the result
        if hasattr(response, 'content') and hasattr(response.content, 'text'):
            email_result = response.content.text
        else:
            email_result = str(response)
            
        return json.dumps({
            "success": True,
            "mom": mom,
            "email_response": email_result
        })
        
    except Exception as e:
        print(f"[ERROR] send_mom failed: {e}")
        import traceback
        traceback.print_exc()
        return json.dumps({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    print("🚀 Starting MoM MCP server...")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type",
        type=str,
        default="sse",
        choices=["sse", "stdio"],
        help="Server type for MCP",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8081,
        help="Port for MoM MCP server",
    )
    args = parser.parse_args()
    server.run(args.server_type, port=args.port)
