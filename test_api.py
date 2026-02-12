"""Test client for Historical Mind-Lab API.

This script demonstrates how to interact with the REST API and WebSocket streaming.
"""

import asyncio
import json
from typing import Dict, Any

import httpx
import websockets


API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"


async def test_rest_api():
    """Test REST API endpoints."""

    print("=" * 80)
    print("REST API TEST")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Test health endpoint
        print("\n1️⃣  Testing health endpoint...")
        response = await client.get(f"{API_BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")

        # Create a new simulation
        print("\n2️⃣  Creating new simulation...")
        create_data = {
            "agent_name": "颜之推 (Yan Zhitui)",
            "birth_year": 531,
            "traits": ["Analytical", "Pragmatic", "Observant"],
            "starting_location": "建康",
            "starting_stress": 40
        }
        response = await client.post(f"{API_BASE_URL}/simulations", json=create_data)
        print(f"   Status: {response.status_code}")

        simulation = response.json()
        simulation_id = simulation["simulation_id"]
        print(f"   Simulation ID: {simulation_id}")
        print(f"   Location: {simulation['location']['name']}")
        print(f"   Stress: {simulation['psychology']['stress']}/100")

        # Get simulation state
        print("\n3️⃣  Getting simulation state...")
        response = await client.get(f"{API_BASE_URL}/simulations/{simulation_id}/state")
        state = response.json()
        print(f"   Status: {state['status']}")
        print(f"   Location: {state['location']['name']} (Danger: {state['location']['danger_level']}/100)")

        # Execute one step
        print("\n4️⃣  Executing one simulation step...")
        response = await client.post(f"{API_BASE_URL}/simulations/{simulation_id}/step")
        step_result = response.json()
        print(f"   Turn: {step_result['turn']}")
        print(f"   Decision: {step_result['decision']['next_action']}")
        print(f"   Reasoning: {step_result['decision']['reasoning'][:80]}...")

        # List all simulations
        print("\n5️⃣  Listing all simulations...")
        response = await client.get(f"{API_BASE_URL}/simulations")
        simulations = response.json()
        print(f"   Total simulations: {len(simulations)}")
        for sim in simulations:
            print(f"   - {sim['simulation_id'][:8]}... | {sim['agent_name']} | {sim['status']}")

        # Get history
        print("\n6️⃣  Getting decision history...")
        response = await client.get(f"{API_BASE_URL}/simulations/{simulation_id}/history")
        history = response.json()
        print(f"   Total decisions: {history['total_decisions']}")
        for i, decision in enumerate(history['history'], 1):
            print(f"   {i}. {decision['action']} - {decision['thought_process'][:60]}...")

        print("\n✅ REST API tests completed!\n")
        return simulation_id


async def test_websocket_streaming(simulation_id: str):
    """Test WebSocket streaming.

    Args:
        simulation_id: ID of simulation to stream.
    """
    print("=" * 80)
    print("WEBSOCKET STREAMING TEST")
    print("=" * 80)

    ws_url = f"{WS_BASE_URL}/ws/simulations/{simulation_id}"
    print(f"\n🔌 Connecting to: {ws_url}")

    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected!")

            # Start the simulation via REST API
            async with httpx.AsyncClient() as client:
                print("\n▶️  Starting simulation...")
                await client.post(f"{API_BASE_URL}/simulations/{simulation_id}/start")

            # Listen for events
            print("\n📡 Streaming events...\n")
            event_count = 0

            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    event = json.loads(message)
                    event_count += 1

                    event_type = event.get("type")
                    data = event.get("data", {})

                    # Print different events
                    if event_type == "connection_established":
                        print(f"🟢 {event_type}: {data.get('message')}")

                    elif event_type == "simulation_started":
                        print(f"🚀 {event_type}: Turn {data.get('turn', 0)}")

                    elif event_type == "turn_start":
                        print(f"\n📍 Turn {data.get('turn')}: {data['state']['location']['name']}")

                    elif event_type == "historical_event":
                        desc = data.get('description', '')[:80]
                        threat = data.get('threat_level', 0)
                        print(f"   🔔 Event (threat={threat}/100): {desc}...")

                    elif event_type == "agent_thinking":
                        print(f"   🤔 Agent thinking... (stress={data.get('stress')}/100)")

                    elif event_type == "agent_decision":
                        action = data.get('action')
                        reasoning = data.get('reasoning', '')[:60]
                        print(f"   💭 Decision: {action}")
                        print(f"      Reasoning: {reasoning}...")

                    elif event_type == "action_executed":
                        if data.get('success'):
                            if 'new_location' in data:
                                print(f"   ✅ Moved to: {data['new_location']}")
                                if data.get('reached_safety'):
                                    print(f"      🎉 SAFE HAVEN REACHED!")
                        else:
                            print(f"   ❌ Action failed: {data.get('error')}")

                    elif event_type == "simulation_completed":
                        print(f"\n🏁 Simulation completed!")
                        print(f"   Final location: {data['location']['name']}")
                        print(f"   Final stress: {data['psychology']['stress']}/100")
                        print(f"   Safe: {data['is_safe']}")
                        break

                    elif event_type == "simulation_error":
                        print(f"\n❌ Simulation error: {data.get('error')}")
                        break

                except asyncio.TimeoutError:
                    print("\n⏱️  Timeout waiting for events")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("\n🔴 WebSocket connection closed")
                    break

            print(f"\n📊 Total events received: {event_count}")
            print("✅ WebSocket streaming test completed!\n")

    except Exception as e:
        print(f"\n❌ WebSocket error: {e}")


async def main():
    """Run all tests."""

    print("\n" + "🏛️" * 40)
    print("HISTORICAL MIND-LAB API TEST SUITE")
    print("🏛️" * 40 + "\n")

    print("⚠️  Make sure the API server is running:")
    print("   python3 src/api/server.py")
    print("   or: uvicorn src.api.server:app --reload\n")

    input("Press Enter to start tests...")

    try:
        # Test REST API first
        simulation_id = await test_rest_api()

        # Test WebSocket streaming
        await test_websocket_streaming(simulation_id)

        print("=" * 80)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 80)

    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API server.")
        print("   Please start the server first:")
        print("   python3 src/api/server.py\n")
    except Exception as e:
        print(f"\n❌ Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
