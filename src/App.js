import { BrowserRouter, Route, Routes } from "react-router-dom";
import { MantineProvider } from "@mantine/core";
import Layout from "./pages/Layout";
import Home from "./pages/Home";
import Browser from "./pages/Browser";
import Map from "./pages/Map";
import NoPage from "./pages/NoPage";


export default function App() {
  return (
    <>
      <MantineProvider withGlobalStyles withNormalizeCSS>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={ <Layout /> }>
              <Route index element={ <Home /> } />
              <Route path="browser" element={ <Browser /> } />
              <Route path="map" element={ <Map /> } />
              <Route path="*" element={ <NoPage /> } />
            </Route>
          </Routes>
        </BrowserRouter>
      </MantineProvider>
    </>
  );
}