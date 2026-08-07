import api from "../api/api";

export interface LoginData {
    email: string;
    senha: string;
}

export async function login(data: LoginData) {
    const response = await api.post("/auth/login", data);

    localStorage.setItem(
        "access_token",
        response.data.access_token
    );
    
    return response.data;
}