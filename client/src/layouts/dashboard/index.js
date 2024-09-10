/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

import axios from "axios";
import { useQuery } from "react-query";

// @mui material components
import Grid from "@mui/material/Grid";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import PieChart from "examples/Charts/PieChart";
import VerticalBarChart from "examples/Charts/BarCharts/VerticalBarChart";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";

import reportsLineChartData from "layouts/dashboard/data/reportsLineChartData";

const fetchData = async () => {
  const headers = {
    "content-type": "application/x-www-form-urlencoded",
  };
  const res = await axios
    .get("https://storage.googleapis.com/spark-netflix-bucket-39/data/netflix.json", headers)
    .then((response) => response.data);
  return res;
};

function Dashboard() {
  const { tasks } = reportsLineChartData;
  const { data, isLoading } = useQuery("getData", fetchData);

  if (isLoading) {
    return <></>;
  }
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="rocket_launch"
                title="Total de Lançamentos"
                count={data.total}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="calendar_month"
                title="Dia com mais Lançamento"
                count={data.day_with_more_additions}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="primary"
                icon="movie"
                title="Média duração de Filmes"
                count={`${Math.round(data.means["duration"])} minuto(s)`}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="slideshow"
                title="Média duração de Séries"
                count={`${Math.round(data.means["seasons"])} temporada(s)`}
              />
            </MDBox>
          </Grid>
        </Grid>
        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <PieChart
                  icon={{ color: "secondary", component: "public" }}
                  title="Lançamentos por País"
                  description="Países com o maior número de lançamentos"
                  chart={{
                    labels: Object.keys(data.top_countries),
                    datasets: {
                      label: "Countries",
                      data: Object.values(data.top_countries),
                      backgroundColors: ["info", "primary", "success", "secondary", "warning"],
                    },
                  }}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <PieChart
                  icon={{ color: "secondary", component: "person" }}
                  title="Lançamentos por Diretor"
                  description="Diretores com o maior número de lançamentos"
                  chart={{
                    labels: Object.keys(data.top_directors),
                    datasets: {
                      label: "Countries",
                      data: Object.values(data.top_directors),
                      backgroundColors: ["info", "primary", "success", "secondary", "warning"],
                    },
                  }}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <PieChart
                  icon={{ color: "secondary", component: "leaderboard" }}
                  title="Lançamento por Tipo"
                  description="Tipos de mídias lançadas"
                  chart={{
                    labels: Object.keys(data.total_types),
                    datasets: {
                      label: "Countries",
                      data: Object.values(data.total_types),
                      backgroundColors: ["info", "primary"],
                    },
                  }}
                />
              </MDBox>
            </Grid>
          </Grid>
          <Grid container spacing={3}>
            <Grid item xs={12} md={12} lg={12}>
              <MDBox mb={3}>
                <VerticalBarChart
                  icon={{ color: "info", component: "calendar_month" }}
                  title="Lançamentos por Ano"
                  description="Total de Filmes e Séries lançados a cada ano"
                  chart={{
                    labels: Object.keys(data.releases),
                    datasets: [
                      {
                        label: "Lançamentos por Ano",
                        color: "dark",
                        data: Object.values(data.releases),
                      },
                    ],
                  }}
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Dashboard;
