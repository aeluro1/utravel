import { Checkbox, Divider, ScrollArea, TextInput, createStyles } from "@mantine/core";
import { useState } from "react";
import { useRefinementList } from "react-instantsearch-hooks-web";


const useStyles = createStyles((theme) => ({
  root: {
    width: "100%",
    display: "flex",
    flexFlow: "column nowrap"
  },
  searchBox: {
    marginBottom: [theme.spacing.xs]
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

  let checkbox = (
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
  )
  
  if (props.scrollable) {
    checkbox = (
      <ScrollArea h={props.h} type="hover" offsetScrollbars>
        {checkbox}
      </ScrollArea>
    )
  }

  return (
    <div className={classes.root}>
      {props.searchable ? (
        <TextInput
          className={classes.searchBox}
          placeholder={props.searchablePlaceholder}
          onChange={(e) => updateSearch(e.target.value)}
        />
      ) : (
        null
      )}
      {checkbox}
      <Divider my="md" />
    </div>
  )
}