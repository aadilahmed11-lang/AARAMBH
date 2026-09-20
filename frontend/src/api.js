import axios from "axios";
export const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";
export const api = axios.create({baseURL:API});
api.interceptors.request.use(c=>{
  const t=localStorage.getItem("aarambh_token");
  if(t)c.headers.Authorization=`Bearer ${t}`;
  return c;
});
