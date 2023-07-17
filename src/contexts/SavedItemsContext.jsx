import { createContext, useEffect, useCallback, useMemo, useState } from "react";


export const savedItemsContext = createContext();

export default function SavedItemsProvider(props) {
  const initState = JSON.parse(localStorage.getItem("savedItems")) || [];
  const [savedItems, setSavedItems] = useState(initState);

  useEffect(() => {
    localStorage.setItem("savedItems", JSON.stringify(savedItems));
  }, [savedItems])

  const addItem = useCallback((item) => {
    setSavedItems([...savedItems, item]);
  }, [savedItems]);

  const delItem = useCallback((id) => {
    setSavedItems(savedItems.filter((item) => (item.id !== id)));
  }, [savedItems])

  const contextValue = useMemo(() => ({
    savedItems,
    addItem,
    delItem
  }), [savedItems, addItem, delItem]);

  return (
    <savedItemsContext.Provider value={contextValue}>
      {props.children}
    </savedItemsContext.Provider>
  )
}