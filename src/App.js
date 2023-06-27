import { useEffect } from "react";
import { BrowserRouter, Route, Routes} from "react-router-dom";
import { MantineProvider, Text } from "@mantine/core";

import Layout from "./pages/Layout";
import Home from "./pages/Home";
import Browser from "./pages/Browser";
import NoPage from "./pages/NoPage"

export default function App() {
  // const [savedItem, setSavedItem] = useState([]);


  return (
    <div>
      <MantineProvider withGlobalStyles withNormalizeCSS>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="browser" element={<Browser />} />
              <Route path="*" element={<NoPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </MantineProvider>
    </div>
  );
}