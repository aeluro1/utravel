import { BrowserRouter, Route, Routes } from "react-router-dom";
import { MantineProvider } from "@mantine/core";
import Layout from "./pages/Layout";
import Home from "./pages/Home";
import Browser from "./pages/Browser.jsx";
import Map from "./pages/Map";
import NoPage from "./pages/NoPage";
import SavedItemsProvider from "contexts/SavedItemsContext";


export default function App() {
  return (
    <>
      <MantineProvider withGlobalStyles withNormalizeCSS>
        <SavedItemsProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={ <Layout /> }>
                <Route index element={ <Home /> } />
                <Route path="browser/:page?" element={ <Browser /> } />
                <Route path="map" element={ <Map /> } />
                <Route path="*" element={ <NoPage /> } />
              </Route>
            </Routes>
          </BrowserRouter>
        </SavedItemsProvider>
      </MantineProvider>
    </>
  );
}