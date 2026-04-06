import "./themeBootstrap";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";
import App from "./App";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useAppStore } from "@/stores/appStore";
import "./styles/globals.css";

function Root() {
  const theme = useAppStore((s) => s.theme);
  return (
    <>
      <App />
      <Toaster
        theme={theme}
        position="bottom-right"
        richColors
        closeButton
      />
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <TooltipProvider delayDuration={300}>
        <Root />
      </TooltipProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
