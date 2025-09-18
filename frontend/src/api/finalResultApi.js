const backendUrl = process.env.REACT_APP_API_URL || "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

const getStoredUsername = () => localStorage.getItem("username");

export const generateFinalResult = async () => {
    const username = getStoredUsername();
    if (!username) {
        console.error("No username found in localStorage.");
        return null;
    }

    try {
        const response = await fetch(`${backendUrl}/generate_final_result/${username}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        return await response.json(); // Returns { message: "Final result generated successfully", final_result: {...} }
    } catch (error) {
        console.error("Error generating final result:", error);
        return null;
    }
};

export const getFinalResult = async () => {
    const username = getStoredUsername();
    if (!username) {
        console.error("No username found in localStorage.");
        return null;
    }

    try {
        const response = await fetch(`${backendUrl}/get_final_result/${username}`);

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        return await response.json(); // Returns the stored final result
    } catch (error) {
        console.error("Error fetching final result:", error);
        return null;
    }
};
