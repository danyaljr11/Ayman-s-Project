// Define the API base URL
const API_BASE = "http://127.0.0.1:8000/api";

function getCSRFToken() {
    const csrfCookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return csrfCookie ? csrfCookie.split("=")[1] : null;
}

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem("access_token");
    const headers = options.headers || {};

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    headers["Content-Type"] = "application/json";

    // Add CSRF Token
    const csrfToken = getCSRFToken();
    if (csrfToken) {
        headers["X-CSRFToken"] = csrfToken;
    }

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
        throw new Error(`Error response: ${await response.text()}`);
    }

    return await response.json();
}

// Register functionality
async function register(event) {
    event.preventDefault();
    const form = event.target;
    const full_name = form.full_name.value.trim();
    const email = form.email.value.trim();
    const primary_phone = form.primary_phone.value.trim();
    const secondary_phone = form.secondary_phone.value.trim();
    const password = form.password.value.trim();

    // Validate form inputs
    if (!full_name || !email || !primary_phone || !secondary_phone || !password) {
        alert("All fields are required.");
        return;
    }

    try {
        // Hardcoded user_type as "guest"
        const user_type = "guest";

        const response = await fetch(`${API_BASE}/register/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                full_name,
                email,
                primary_phone,
                secondary_phone,
                password,
                user_type
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            console.error("Registration error:", data);
            alert(data.error || "Registration failed. Please check your inputs and try again.");
            return;
        }

        alert("Registration successful! Please log in.");
        window.location.href = "/login/";
    } catch (error) {
        console.error("Registration error:", error);
        alert("An error occurred during registration. Please try again.");
    }
}

// Login functionality
async function login(event) {
    event.preventDefault();
    const form = event.target;
    const email = form.email.value;
    const password = form.password.value;

    try {
        const response = await fetch(`${API_BASE}/login/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Login failed. Invalid credentials.");
        }

        const data = await response.json();

        // Check if access token and user data exist
        if (!data.access || !data.user || !data.user.user_type) {
            throw new Error("Unexpected server response. Please try again.");
        }

        // Save tokens and user type to localStorage
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        localStorage.setItem("user_type", data.user.user_type);

        // Redirect based on user type
        if (data.user.user_type === "guest") {
            window.location.href = "/guest/home/";
        } else if (data.user.user_type === "employee") {
            window.location.href = "/employee/home/";
        } else {
            throw new Error("Invalid user type.");
        }

    } catch (error) {
        console.error("Login error:", error);
        alert(error.message || "Login failed. Please check your credentials.");
    }
}


// Logout functionality
async function logout() {
    try {
        // Attempt logout API call
        await fetchWithAuth(`${API_BASE}/logout/`, { method: "POST" });
    } catch (error) {
        console.warn("Server logout failed. Clearing tokens locally.");
    } finally {
        // Clear tokens from localStorage
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user_type");
        window.location.href = "/login/";
    }
}

// Add a new request
// Add a new request
async function addRequest(event) {
    event.preventDefault();
    const form = event.target;
    const type = form.type.value;
    const description = form.description.value;
    const employeeId = form.employee.value;

    try {
        await fetchWithAuth(`${API_BASE}/requests/create/`, {
            method: "POST",
            body: JSON.stringify({ type, description, employee: employeeId }),
        });
        alert("Request created successfully!");
        window.location.href = "/guest/home/";
    } catch (error) {
        alert("Failed to create request.");
    }
}

// Populate guest requests
async function populateGuestRequests() {
    const listElement = document.getElementById("guest-requests");
    const noRequestsMessage = document.getElementById("no-requests-message");

    try {
        const requests = await fetchWithAuth(`${API_BASE}/requests/list/`);
        listElement.innerHTML = "";

        if (!requests.length) {
            noRequestsMessage.style.display = "block";
            return;
        }

        noRequestsMessage.style.display = "none";
        requests.forEach((request) => {
            const assignedEmployee = request.employee ? request.employee_name || "N/A" : "N/A";
            const listItem = document.createElement("li");
            listItem.classList.add("list-group-item");
            listItem.innerHTML = `
                <strong>Type:</strong> ${request.type}<br>
                <strong>Status:</strong> ${request.status}<br>
                <strong>Description:</strong> ${request.description}<br>
                <strong>Assigned Employee:</strong> ${assignedEmployee}
            `;
            listElement.appendChild(listItem);
        });
    } catch (error) {
        console.error("Error fetching guest requests:", error);
        alert("Failed to load requests. Please try again later.");
    }
}

// Populate employee requests
async function populateEmployeeRequests() {
    const container = document.getElementById("requests-container");

    try {
        const requests = await fetchWithAuth(`${API_BASE}/requests/list/`);
        container.innerHTML = "";

        requests.forEach((request) => {
            const card = document.createElement("div");
            card.classList.add("request-card");
            card.innerHTML = `
                <p><strong>Type:</strong> ${request.type}</p>
                <p><strong>Status:</strong>
                    <select data-id="${request.id}" class="request-status">
                        <option value="open" ${request.status === "open" ? "selected" : ""}>Open</option>
                        <option value="on process" ${request.status === "on process" ? "selected" : ""}>On Process</option>
                        <option value="closed" ${request.status === "closed" ? "selected" : ""}>Closed</option>
                    </select>
                </p>
                <p><strong>Description:</strong> ${request.description}</p>
                <textarea placeholder="Add notes">${request.notes || ""}</textarea>
                <button data-id="${request.id}" class="update-request">Update</button>
            `;
            container.appendChild(card);
        });

        document.querySelectorAll(".request-status").forEach((dropdown) => {
            dropdown.addEventListener("change", handleStatusChange);
        });

        document.querySelectorAll(".update-request").forEach((button) => {
            button.addEventListener("click", updateRequest);
        });
    } catch (error) {
        console.error("Error loading employee requests:", error);
        alert("Failed to load employee requests.");
    }
}


async function handleStatusChange(event) {
    const requestId = event.target.dataset.id;
    const status = event.target.value;

    try {
        await fetchWithAuth(`${API_BASE}/requests/${requestId}/edit/`, {
            method: "PATCH",
            body: JSON.stringify({ status }),
        });
        alert("Request status updated successfully.");
    } catch (error) {
        console.error("Error updating status:", error);
        alert("Failed to update request status.");
    }
}


async function updateRequest(event) {
    const button = event.target;
    const card = button.closest(".request-card");
    const requestId = button.dataset.id;
    const status = card.querySelector(".request-status").value;
    const notes = card.querySelector("textarea").value;

    try {
        await fetchWithAuth(`${API_BASE}/requests/${requestId}/edit/`, {
            method: "PATCH",
            body: JSON.stringify({ status, notes }),
        });
        alert("Request updated successfully.");
        window.location.reload();
    } catch (error) {
        console.error("Error updating request:", error);
        alert("Failed to update the request.");
    }
}

// Populate employee dropdown for request form
async function populateEmployeeDropdown() {
    const dropdown = document.getElementById("employee-dropdown");

    try {
        const employees = await fetchWithAuth(`${API_BASE}/employees/`);
        dropdown.innerHTML = "<option value=''>Select Employee</option>";
        employees.forEach(employee => {
            const option = document.createElement("option");
            option.value = employee.id;
            option.textContent = employee.full_name;
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching employees:", error);
        alert("Failed to load employee list.");
    }
}

function initializePage() {
    const path = window.location.pathname;

    if (localStorage.getItem("access_token")) {
        if (path === "/guest/home/") populateGuestRequests();
        if (path === "/employee/home/") populateEmployeeRequests();
        if (path === "/requests/add/") populateEmployeeDropdown();
    }

    document.getElementById("login-form")?.addEventListener("submit", login);
    document.getElementById("register-form")?.addEventListener("submit", register);
    document.getElementById("logout-button")?.addEventListener("click", logout);
    const addRequestForm = document.getElementById("add-request-form");
    if (addRequestForm) addRequestForm.addEventListener("submit", addRequest);
}

document.addEventListener("DOMContentLoaded", initializePage);
