import React from 'react';
import { Kovan, DAppProvider } from '@usedapp/core'
import { Container } from "@material-ui/core"
import { Header } from "./components/Header"
import { Main } from "./components/Main"


function App() {
  return (
    <DAppProvider config={{
      networks: [Kovan],
      notifications: {
        expirationPeriod: 1000,
        checkInterval: 1000
      }
    }}>
      <Header />
      <Container maxWidth="md">
        <Main />
      </Container>
    </DAppProvider>
  );
}

export default App;
