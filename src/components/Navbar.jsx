// Template from Mantine docs

import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  createStyles,
  Header,
  Group,
  Burger,
  Paper,
  Transition,
  rem,
  Container,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { links } from "components/Links";


export const HEADER_HEIGHT = rem(60);

const useStyles = createStyles((theme) => ({
  root: {
    position: 'fixed',
    zIndex: 1,
    width: "100vw",
    // overflowX: "hidden"
  },

  dropdown: {
    position: 'absolute',
    top: HEADER_HEIGHT,
    left: 0,
    right: 0,
    zIndex: 0,
    borderTopRightRadius: 0,
    borderTopLeftRadius: 0,
    borderTopWidth: 0,
    overflow: 'hidden',

    [theme.fn.largerThan('sm')]: {
      display: 'none',
    },
  },

  header: {
    height: "100%",
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },

  links: {
    [theme.fn.smallerThan('sm')]: {
      display: 'none',
    },
  },

  burger: {
    [theme.fn.largerThan('sm')]: {
      display: 'none',
    },
  },

  link: {
    display: 'block',
    lineHeight: 1,
    padding: `${rem(8)} ${rem(12)}`,
    borderRadius: theme.radius.sm,
    textDecoration: 'none',
    color: theme.colorScheme === 'dark' ? theme.colors.dark[0] : theme.colors.gray[7],
    fontSize: theme.fontSizes.sm,
    fontWeight: 500,

    '&:hover': {
      backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[6] : theme.colors.gray[0],
    },

    [theme.fn.smallerThan('sm')]: {
      borderRadius: 0,
      padding: theme.spacing.md,
    },
  },

  linkActive: {
    '&, &:hover': {
      backgroundColor: theme.fn.variant({ variant: 'light', color: theme.primaryColor }).background,
      color: theme.fn.variant({ variant: 'light', color: theme.primaryColor }).color,
    },
  },
}));

export default function Navbar() {
  const [opened, handlers] = useDisclosure(false);
  const loc = useLocation();
  const [active, setActive] = useState(loc.pathname);
  const { classes, cx } = useStyles();

  useEffect(() => {
    setActive(loc.pathname)
  }, [loc])

  const items = links.map((link) => (
    <Link
      key={link.label}
      to={link.link}
      className={cx(classes.link, { [classes.linkActive]: active === link.link })}
      onClick={(event) => {
        // event.preventDefault();
        setActive(link.link);
        handlers.close();
      }}
    >
      {link.label}
    </Link>
  ));

  return (
    <Header height={HEADER_HEIGHT} className={classes.root}>
      <Container className={classes.header}>
        <Group spacing="sm" className={classes.links}>
          {items}
        </Group>

        <Burger opened={opened} onClick={handlers.toggle} className={classes.burger} size="sm" />

        <Transition transition="pop-top-right" duration={200} mounted={opened}>
          {(styles) => (
            <Paper className={classes.dropdown} withBorder style={styles}>
              {items}
            </Paper>
          )}
        </Transition>
      </Container>
    </Header>
  );
}