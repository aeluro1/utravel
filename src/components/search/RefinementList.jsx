import { Checkbox, ScrollArea, TextInput, createStyles } from "@mantine/core";
import { useState } from "react";
import { useRefinementList } from "react-instantsearch-hooks-web";


const useStyles = createStyles((theme) => ({
  root: {
    height: "min(min-content, 300px)",
    width: "100%"
  }
}))

export default function RefinementList(props) {
  const { classes } = useStyles();
  const {
    items,
    refine,
    searchForItems
  } = useRefinementList(props);
  const [facets, setFacets] = useState([]);

  const updateSearch = (query) => {
    searchForItems(query);
  }

  const updateRefinement = (newFacets) => {
    if (newFacets.length > facets.length) {
      refine(newFacets[newFacets.length - 1]);
    } else {
      for (const i of facets) {
        if (!newFacets.includes(i)) {
          refine(i);
        }
      }
    }
    updateSearch("");
    setFacets(newFacets);
  }

  return (
    <div>
      <TextInput
        placeholder={props.searchablePlaceholder}
        onChange={(e) => updateSearch(e.target.value)}
      />
      <ScrollArea h={props.h} className={classes.root} type="hover" offsetScrollbars>
        <Checkbox.Group onChange={updateRefinement}>
          {items.map((item) => (
            <Checkbox
              key={item.value}
              value={item.label}
              label={`${item.label} (${item.count})`}
              size="xs"
              checked={item.isRefined}
            />
          ))}
        </Checkbox.Group>
      </ScrollArea>
    </div>
  )
}