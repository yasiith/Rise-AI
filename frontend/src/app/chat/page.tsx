"use client";
import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import Chatbot from "../components/Chat";

const page = () => {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
    }
  }, [router]);

  return (
    <div>
      <Chatbot />
    </div>
  );
};

export default page;
