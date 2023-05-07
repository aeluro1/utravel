import { useState, useEffect } from "react";
import { Route, Routes} from "react-dom";
import { MantineProvider, Text } from "@mantine/core";

import Navbar from "./Navbar";
import Home from "./pages/Home";
import Map from "./pages/Map";
import Browser from "./pages/Browser";

export default function App() {
  const [savedItem, setSavedItem] = useState([]);

  useEffect(() => {
    
  })

  return (
    <div>
      <MantineProvider withGlobalStyles withNormalizeCSS>
        <Navbar />
        <Text>Mantine!</Text>
      </MantineProvider>
      <Routes>
        <Route index path="/" element={<Home />} />
        <Route path="/map" element={<Map />} />
        <Route path="items" element={<Browser />} />
      </Routes>
    </div>

  );
}