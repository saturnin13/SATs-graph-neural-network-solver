FROM pytorch/pytorch

COPY ./src /SATs-graph-neural-network-solver/src
COPY ./experiments_results /SATs-graph-neural-network-solver/experiments_results
COPY ./scripts /SATs-graph-neural-network-solver/scripts
COPY ./requirements.txt /SATs-graph-neural-network-solver/requirements.txt

WORKDIR /SATs-graph-neural-network-solver

RUN pip3 install --no-cache-dir -r requirements.txt
RUN ./scripts/setup.sh

CMD [ "python", "./src/main.py" ]