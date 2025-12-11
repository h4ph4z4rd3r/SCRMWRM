# Phase 5: The War Room UI Design

## 1. User Journey & Philosophy

**"The Morning Coffee Review"**
The Contract Manager starts their day viewing the **Dashboard**. They don't want to dig into 50 files. They want to know:
1.  Who replied overnight?
2.  Which high-risk deals are stalled?
3.  Where is my "Agency" needed? (Approvals vs Information)

**"Proactive Control"**
The system is not just a chat bot. It is a **State Machine Visualizer**. Every negotiation is in a clear state (e.g., `analyzing`, `waiting_on_supplier`, `needs_approval`).

## 2. Views & Experience

### 2.1 The Command Dashboard (`/dashboard`)
A high-density view to manage the portfolio of negotiations.

*   **Layout**: Kanban Board or Smart List (User toggleable).
*   **Columns/Filters**:
    *   🔴 **Action Required**: Agent has drafted a response/strategy and halted for `Confimration` (Strict/Medium mode).
    *   🟡 **In Progress**: Agent is thinking or waiting on internal steps.
    *   🔵 **Waiting on Supplier**: Message sent, waiting for reply.
    *   🟢 **Closed**: Signed or Dead.
*   **Card Metadata**:
    *   Supplier Name & Risk Score (e.g., "Acme Corp (Risk: 85 - HIGH)").
    *   Last Activity: "Received redline 2h ago".
    *   Next Step: "Approve Counter-Offer".

### 2.2 The War Room (`/negotiation/{id}`)
The deep-dive focus mode for a single case.

**Three-Pane Layout**:

**Left Pane: Intelligence Context**
*   **Supplier Scorecard**: Financial Health, News Sentiment, Performance (Quality/Delivery).
*   **Policy Constraints**: List of active policies irrelevant to this contract (e.g., "Violating Payment Terms Policy").

**Center Pane: The Timeline (Chat & Action)**
*   **Chronological Feed**:
    *   *User (Tuesday)*: "Sent Draft v1."
    *   *Supplier (Wednesday)*: "Email received: We need Net 30." (Manually pasted or via API).
    *   *Agent (Wednesday)*: "Analysis: Net 30 violates Policy. Risk is High. Strategy: Counter with Net 45."
    *   **Action Block**: A distinct UI element showing the "Pending Decision".
        *   Buttons: `[ Approve Strategy ]` `[ Edit Strategy ]` `[ Override ]`.
*   **Input Area**:
    *   "Paste Email/Message Context Here" (Initial MPV).
    *   "Guidance/Feedback" (Human feedback loop).

**Right Pane: The Document (The artifact)**
*   **Current Draft**: The actual legal text.
*   **Diff View**: Red vs Green highlighting of changes proposed by the Agent vs the Supplier.
*   *Interactive*: Clicking a clause in list jumps to text here.

## 3. Interaction Flow (MVP)

1.  **Trigger**: User receives an email from Supplier with a redlined `.docx` or simple text.
2.  **Input**: User goes to `/negotiation/{id}`, pastes the text/uploads file into the chat input.
3.  **Processing**:
    *   UI shows "Agent is thinking..." (Polling `POST /agent/negotiate`).
    *   Backend runs LangGraph (Lawyer -> Analyst -> Negotiator).
4.  **Interruption (HITL)**:
    *   Graph hits `GatekeeperNode`. Returns `status: paused`.
    *   UI identifies paused state. Displays the **Strategy Card**: *"I plan to Reject this. Reason: Policy X."*
5.  **Review**:
    *   User clicks `Approve`.
    *   UI calls `POST /agent/resume` with `action: APPROVED`.
6.  **Completion**:
    *   Agent resumes, runs `DraftingNode`.
    *   UI updates with the final drafted response: *"Here is the email to send..."*

## 4. Technical Architecture (Frontend)

*   **Framework**: React 18 (Vite).
*   **Styling**: Tailwind CSS (Dark Mode default for "War Room" aesthetic).
*   **State Management**: React Query (TanStack Query) for polling backend state.
*   **Icons**: Lucide React.
*   **Routing**: React Router.

## 5. Implementation Plan

1.  **Scaffold**: Initialize Vite project `frontend`.
2.  **API Client**: Generate/Manual fetch wrapper for Backend endpoints (`/supplier`, `/agent`).
3.  **Components**:
    *   `RiskBadge`, `PolicyCard`.
    *   `ChatInterface` (Message bubbles).
    *   `NegotiationBoard` (Kanban).
4.  **Pages**:
    *   `DashboardPage`.
    *   `NegotiationPage`.
5.  **Integration**: Connect to `POST /agent/negotiate` and handle the polling mechanism for the Graph.
