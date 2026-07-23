import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DashboardLayout } from "./layouts/DashboardLayout";
import { OverviewPage } from "./pages/overview/OverviewPage";
import { WhatsAppPage } from "./pages/whatsapp/WhatsAppPage";
import { Mt5Page } from "./pages/mt5/Mt5Page";
import { CampaignsPage } from "./pages/campaigns/CampaignsPage";
import { CampaignDetailPage } from "./pages/campaigns/CampaignDetailPage";
import { ConfirmationsPage } from "./pages/confirmations/ConfirmationsPage";
import { OrdersPositionsPage } from "./pages/positions/OrdersPositionsPage";
import { EventsPage } from "./pages/events/EventsPage";
import { SettingsPage } from "./pages/settings/SettingsPage";
import { AboutPage } from "./pages/about/AboutPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 3000,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<OverviewPage />} />
            <Route path="whatsapp" element={<WhatsAppPage />} />
            <Route path="mt5" element={<Mt5Page />} />
            <Route path="campaigns" element={<CampaignsPage />} />
            <Route path="campaigns/:id" element={<CampaignDetailPage />} />
            <Route path="confirmations" element={<ConfirmationsPage />} />
            <Route path="positions" element={<OrdersPositionsPage />} />
            <Route path="events" element={<EventsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="about" element={<AboutPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
