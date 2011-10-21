# interfaces.py
# Copyright (C) 2005, 2006, 2007, 2008, 2009 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""

Semi-private module containing various base classes used throughout the ORM.

Defines the extension classes :class:`MapperExtension`,
:class:`SessionExtension`, and :class:`AttributeExtension` as
well as other user-subclassable extension objects.

"""

from itertools import chain

import sqlalchemy.exceptions as sa_exc
from sqlalchemy import log, util
from sqlalchemy.sql import expression

class_mapper = None
collections = None

__all__ = (
    'AttributeExtension',
    'EXT_CONTINUE',
    'EXT_STOP',
    'ExtensionOption',
    'InstrumentationManager',
    'LoaderStrategy',
    'MapperExtension',
    'MapperOption',
    'MapperProperty',
    'PropComparator',
    'PropertyOption',
    'SessionExtension',
    'StrategizedOption',
    'StrategizedProperty',
    'build_path',
    )

EXT_CONTINUE = util.symbol('EXT_CONTINUE')
EXT_STOP = util.symbol('EXT_STOP')

ONETOMANY = util.symbol('ONETOMANY')
MANYTOONE = util.symbol('MANYTOONE')
MANYTOMANY = util.symbol('MANYTOMANY')

class MapperExtension(object):
    """Base implementation for customizing Mapper behavior.

    For each method in MapperExtension, returning a result of EXT_CONTINUE
    will allow processing to continue to the next MapperExtension in line or
    use the default functionality if there are no other extensions.

    Returning EXT_STOP will halt processing of further extensions handling
    that method.  Some methods such as ``load`` have other return
    requirements, see the individual documentation for details.  Other than
    these exception cases, any return value other than EXT_CONTINUE or
    EXT_STOP will be interpreted as equivalent to EXT_STOP.

    """
    def instrument_class(self, mapper, class_):
        return EXT_CONTINUE

    def init_instance(self, mapper, class_, oldinit, instance, args, kwargs):
        return EXT_CONTINUE

    def init_failed(self, mapper, class_, oldinit, instance, args, kwargs):
        return EXT_CONTINUE

    def translate_row(self, mapper, context, row):
        """Perform pre-processing on the given result row and return a
        new row instance.

        This is called when the mapper first receives a row, before
        the object identity or the instance itself has been derived
        from that row.

        """
        return EXT_CONTINUE

    def create_instance(self, mapper, selectcontext, row, class_):
        """Receive a row when a new object instance is about to be
        created from that row.

        The method can choose to create the instance itself, or it can return
        EXT_CONTINUE to indicate normal object creation should take place.

        mapper
          The mapper doing the operation

        selectcontext
          SelectionContext corresponding to the instances() call

        row
          The result row from the database

        class\_
          The class we are mapping.

        return value
          A new object instance, or EXT_CONTINUE

        """
        return EXT_CONTINUE

    def append_result(self, mapper, selectcontext, row, instance, result, **flags):
        """Receive an object instance before that instance is appended
        to a result list.

        If this method returns EXT_CONTINUE, result appending will proceed
        normally.  if this method returns any other value or None,
        result appending will not proceed for this instance, giving
        this extension an opportunity to do the appending itself, if
        desired.

        mapper
          The mapper doing the operation.

        selectcontext
          SelectionContext corresponding to the instances() call.

        row
          The result row from the database.

        instance
          The object instance to be appended to the result.

        result
          List to which results are being appended.

        \**flags
          extra information about the row, same as criterion in
          ``create_row_processor()`` method of :class:`~sqlalchemy.orm.interfaces.MapperProperty`
        """

        return EXT_CONTINUE

    def populate_instance(self, mapper, selectcontext, row, instance, **flags):
        """Receive an instance before that instance has
        its attributes populated.

        This usually corresponds to a newly loaded instance but may
        also correspond to an already-loaded instance which has
        unloaded attributes to be populated.  The method may be called
        many times for a single instance, as multiple result rows are
        used to populate eagerly loaded collections.

        If this method returns EXT_CONTINUE, instance population will
        proceed normally.  If any other value or None is returned,
        instance population will not proceed, giving this extension an
        opportunity to populate the instance itself, if desired.

        As of 0.5, most usages of this hook are obsolete.  For a
        generic "object has been newly created from a row" hook, use
        ``reconstruct_instance()``, or the ``@orm.reconstructor``
        decorator.

        """
        return EXT_CONTINUE

    def reconstruct_instance(self, mapper, instance):
        """Receive an object instance after it has been created via
        ``__new__``, and after initial attribute population has
        occurred.

        This typically occurs when the instance is created based on
        incoming result rows, and is only called once for that
        instance's lifetime.

        Note that during a result-row load, this method is called upon
        the first row received for this instance. If eager loaders are
        set to further populate collections on the instance, those
        will *not* yet be completely loaded.

        """
        return EXT_CONTINUE

    def before_insert(self, mapper, connection, instance):
        """Receive an object instance before that instance is INSERTed
        into its table.

        This is a good place to set up primary key values and such
        that aren't handled otherwise.

        Column-based attributes can be modified within this method
        which will result in the new value being inserted.  However
        *no* changes to the overall flush plan can be made; this means
        any collection modification or save() operations which occur
        within this method will not take effect until the next flush
        call.

        """

        return EXT_CONTINUE

    def after_insert(self, mapper, connection, instance):
        """Receive an object instance after that instance is INSERTed."""

        return EXT_CONTINUE

    def before_update(self, mapper, connection, instance):
        """Receive an object instance before that instance is UPDATEed.

        Note that this method is called for all instances that are marked as
        "dirty", even those which have no net changes to their column-based
        attributes.  An object is marked as dirty when any of its column-based
        attributes have a "set attribute" operation called or when any of its
        collections are modified.  If, at update time, no column-based attributes
        have any net changes, no UPDATE statement will be issued.  This means
        that an instance being sent to before_update is *not* a guarantee that
        an UPDATE statement will be issued (although you can affect the outcome
        here).

        To detect if the column-based attributes on the object have net changes,
        and will therefore generate an UPDATE statement, use
        ``object_session(instance).is_modified(instance, include_collections=False)``.

        Column-based attributes can be modified within this method which will
        result in their being updated.  However *no* changes to the overall
        flush plan can be made; this means any collection modification or
        save() operations which occur within this method will not take effect
        until the next flush call.

        """

        return EXT_CONTINUE

    def after_update(self, mapper, connection, instance):
        """Receive an object instance after that instance is UPDATEed."""

        return EXT_CONTINUE

    def before_delete(self, mapper, connection, instance):
        """Receive an object instance before that instance is DELETEed.

        Note that *no* changes to the overall
        flush plan can be made here; this means any collection modification,
        save() or delete() operations which occur within this method will
        not take effect until the next flush call.

        """

        return EXT_CONTINUE

    def after_delete(self, mapper, connection, instance):
        """Receive an object instance after that instance is DELETEed."""

        return EXT_CONTINUE

class SessionExtension(object):
    """An extension hook object for Sessions.  Subclasses may be installed into a Session
    (or sessionmaker) using the ``extension`` keyword argument.
    """

    def before_commit(self, session):
        """Execute right before commit is called.

        Note that this may not be per-flush if a longer running transaction is ongoing."""

    def after_commit(self, session):
        """Execute after a commit has occured.

        Note that this may not be per-flush if a longer running transaction is ongoing."""

    def after_rollback(self, session):
        """Execute after a rollback has occured.

        Note that this may not be per-flush if a longer running transaction is ongoing."""

    def before_flush(self, session, flush_context, instances):
        """Execute before flush process has started.

        `instances` is an optional list of objects which were passed to the ``flush()``
        method.
        """

    def after_flush(self, session, flush_context):
        """Execute after flush has completed, but before commit has been called.

        Note that the session's state is still in pre-flush, i.e. 'new', 'dirty',
        and 'deleted' lists still show pre-flush state as well as the history
        settings on instance attributes."""

    def after_flush_postexec(self, session, flush_context):
        """Execute after flush has completed, and after the post-exec state occurs.

        This will be when the 'new', 'dirty', and 'deleted' lists are in their final
        state.  An actual commit() may or may not have occured, depending on whether or not
        the flush started its own transaction or participated in a larger transaction.
        """

    def after_begin(self, session, transaction, connection):
        """Execute after a transaction is begun on a connection

        `transaction` is the SessionTransaction. This method is called after an
        engine level transaction is begun on a connection.
        """

    def after_attach(self, session, instance):
        """Execute after an instance is attached to a session.

        This is called after an add, delete or merge.
        """

    def after_bulk_update(self, session, query, query_context, result):
        """Execute after a bulk update operation to the session.

        This is called after a session.query(...).update()

        `query` is the query object that this update operation was called on.
        `query_context` was the query context object.
        `result` is the result object returned from the bulk operation.
        """

    def after_bulk_delete(self, session, query, query_context, result):
        """Execute after a bulk delete operation to the session.

        This is called after a session.query(...).delete()

        `query` is the query object that this delete operation was called on.
        `query_context` was the query context object.
        `result` is the result object returned from the bulk operation.
        """

class MapperProperty(object):
    """Manage the relationship of a ``Mapper`` to a single class
    attribute, as well as that attribute as it appears on individual
    instances of the class, including attribute instrumentation,
    attribute access, loading behavior, and dependency calculations.
    """

    def setup(self, context, entity, path, adapter, **kwargs):
        """Called by Query for the purposes of constructing a SQL statement.

        Each MapperProperty associated with the target mapper processes the
        statement referenced by the query context, adding columns and/or
        criterion as appropriate.
        """

        pass

    def create_row_processor(self, selectcontext, path, mapper, row, adapter):
        """Return a 2-tuple consiting of two row processing functions and an instance post-processing function.

        Input arguments are the query.SelectionContext and the *first*
        applicable row of a result set obtained within
        query.Query.instances(), called only the first time a particular
        mapper's populate_instance() method is invoked for the overall result.

        The settings contained within the SelectionContext as well as the
        columns present in the row (which will be the same columns present in
        all rows) are used to determine the presence and behavior of the
        returned callables.  The callables will then be used to process all
        rows and instances.

        Callables are of the following form::

            def new_execute(state, dict_, row, **flags):
                # process incoming instance state and given row.  the instance is
                # "new" and was just created upon receipt of this row.
                # flags is a dictionary containing at least the following
                # attributes:
                #   isnew - indicates if the instance was newly created as a
                #           result of reading this row
                #   instancekey - identity key of the instance

            def existing_execute(state, dict_, row, **flags):
                # process incoming instance state and given row.  the instance is
                # "existing" and was created based on a previous row.

            return (new_execute, existing_execute)

        Either of the three tuples can be ``None`` in which case no function
        is called.
        """

        raise NotImplementedError()

    def cascade_iterator(self, type_, state, visited_instances=None, halt_on=None):
        """Iterate through instances related to the given instance for
        a particular 'cascade', starting with this MapperProperty.

        See PropertyLoader for the related instance implementation.
        """

        return iter(())

    def set_parent(self, parent):
        self.parent = parent

    def instrument_class(self, mapper):
        raise NotImplementedError()

    _compile_started = False
    _compile_finished = False

    def init(self):
        """Called after all mappers are created to assemble
        relationships between mappers and perform other post-mapper-creation
        initialization steps.

        """
        self._compile_started = True
        self.do_init()
        self._compile_finished = True

    def do_init(self):
        """Perform subclass-specific initialization post-mapper-creation steps.

        This is a *template* method called by the
        ``MapperProperty`` object's init() method.

        """
        pass

    def post_instrument_class(self, mapper):
        """Perform instrumentation adjustments that need to occur
        after init() has completed.

        """
        pass

    def register_dependencies(self, *args, **kwargs):
        """Called by the ``Mapper`` in response to the UnitOfWork
        calling the ``Mapper``'s register_dependencies operation.
        Establishes a topological dependency between two mappers
        which will affect the order in which mappers persist data.

        """

        pass

    def register_processors(self, *args, **kwargs):
        """Called by the ``Mapper`` in response to the UnitOfWork
        calling the ``Mapper``'s register_processors operation.
        Establishes a processor object between two mappers which
        will link data and state between parent/child objects.

        """

        pass

    def is_primary(self):
        """Return True if this ``MapperProperty``'s mapper is the
        primary mapper for its class.

        This flag is used to indicate that the ``MapperProperty`` can
        define attribute instrumentation for the class at the class
        level (as opposed to the individual instance level).
        """

        return not self.parent.non_primary

    def merge(self, session, source, dest, dont_load, _recursive):
        """Merge the attribute represented by this ``MapperProperty``
        from source to destination object"""

        raise NotImplementedError()

    def compare(self, operator, value):
        """Return a compare operation for the columns represented by
        this ``MapperProperty`` to the given value, which may be a
        column value or an instance.  'operator' is an operator from
        the operators module, or from sql.Comparator.

        By default uses the PropComparator attached to this MapperProperty
        under the attribute name "comparator".
        """

        return operator(self.comparator, value)

class PropComparator(expression.ColumnOperators):
    """defines comparison operations for MapperProperty objects.

    PropComparator instances should also define an accessor 'property'
    which returns the MapperProperty associated with this
    PropComparator.
    """

    def __init__(self, prop, mapper, adapter=None):
        self.prop = self.property = prop
        self.mapper = mapper
        self.adapter = adapter

    def __clause_element__(self):
        raise NotImplementedError("%r" % self)

    def adapted(self, adapter):
        """Return a copy of this PropComparator which will use the given adaption function
        on the local side of generated expressions.

        """
        return self.__class__(self.prop, self.mapper, adapter)

    @staticmethod
    def any_op(a, b, **kwargs):
        return a.any(b, **kwargs)

    @staticmethod
    def has_op(a, b, **kwargs):
        return a.has(b, **kwargs)

    @staticmethod
    def of_type_op(a, class_):
        return a.of_type(class_)

    def of_type(self, class_):
        """Redefine this object in terms of a polymorphic subclass.

        Returns a new PropComparator from which further criterion can be evaluated.

        e.g.::

            query.join(Company.employees.of_type(Engineer)).\\
               filter(Engineer.name=='foo')

        \class_
            a class or mapper indicating that criterion will be against
            this specific subclass.


        """

        return self.operate(PropComparator.of_type_op, class_)

    def any(self, criterion=None, **kwargs):
        """Return true if this collection contains any member that meets the given criterion.

        criterion
          an optional ClauseElement formulated against the member class' table
          or attributes.

        \**kwargs
          key/value pairs corresponding to member class attribute names which
          will be compared via equality to the corresponding values.
        """

        return self.operate(PropComparator.any_op, criterion, **kwargs)

    def has(self, criterion=None, **kwargs):
        """Return true if this element references a member which meets the given criterion.

        criterion
          an optional ClauseElement formulated against the member class' table
          or attributes.

        \**kwargs
          key/value pairs corresponding to member class attribute names which
          will be compared via equality to the corresponding values.
        """

        return self.operate(PropComparator.has_op, criterion, **kwargs)


class StrategizedProperty(MapperProperty):
    """A MapperProperty which uses selectable strategies to affect
    loading behavior.

    There is a single default strategy selected by default.  Alternate
    strategies can be selected at Query time through the usage of
    ``StrategizedOption`` objects via the Query.options() method.
    """

    def __get_context_strategy(self, context, path):
        cls = context.attributes.get(("loaderstrategy", path), None)
        if cls:
            try:
                return self.__all_strategies[cls]
            except KeyError:
                return self.__init_strategy(cls)
        else:
            return self.strategy

    def _get_strategy(self, cls):
        try:
            return self.__all_strategies[cls]
        except KeyError:
            return self.__init_strategy(cls)

    def __init_strategy(self, cls):
        self.__all_strategies[cls] = strategy = cls(self)
        strategy.init()
        return strategy

    def setup(self, context, entity, path, adapter, **kwargs):
        self.__get_context_strategy(context, path + (self.key,)).setup_query(context, entity, path, adapter, **kwargs)

    def create_row_processor(self, context, path, mapper, row, adapter):
        return self.__get_context_strategy(context, path + (self.key,)).create_row_processor(context, path, mapper, row, adapter)

    def do_init(self):
        self.__all_strategies = {}
        self.strategy = self.__init_strategy(self.strategy_class)

    def post_instrument_class(self, mapper):
        if self.is_primary():
            self.strategy.init_class_attribute(mapper)

def build_path(entity, key, prev=None):
    if prev:
        return prev + (entity, key)
    else:
        return (entity, key)

def serialize_path(path):
    if path is None:
        return None

    return [
        (mapper.class_, key)
        for mapper, key in [(path[i], path[i+1]) for i in range(0, len(path)-1, 2)]
    ]

def deserialize_path(path):
    if path is None:
        return None

    global class_mapper
    if class_mapper is None:
        from sqlalchemy.orm import class_mapper

    return tuple(
        chain(*[(class_mapper(cls), key) for cls, key in path])
    )

class MapperOption(object):
    """Describe a modification to a Query."""

    def process_query(self, query):
        pass

    def process_query_conditionally(self, query):
        """same as process_query(), except that this option may not apply
        to the given query.

        Used when secondary loaders resend existing options to a new
        Query."""
        self.process_query(query)

class ExtensionOption(MapperOption):
    """a MapperOption that applies a MapperExtension to a query operation."""

    def __init__(self, ext):
        self.ext = ext

    def process_query(self, query):
        entity = query._generate_mapper_zero()
        entity.extension = entity.extension.copy()
        entity.extension.push(self.ext)

class PropertyOption(MapperOption):
    """A MapperOption that is applied to a property off the mapper or
    one of its child mappers, identified by a dot-separated key.
    """

    def __init__(self, key, mapper=None):
        self.key = key
        self.mapper = mapper

    def process_query(self, query):
        self._process(query, True)

    def process_query_conditionally(self, query):
        self._process(query, False)

    def _process(self, query, raiseerr):
        paths = self.__get_paths(query, raiseerr)
        if paths:
            self.process_query_property(query, paths)

    def process_query_property(self, query, paths):
        pass

    def __find_entity(self, query, mapper, raiseerr):
        from sqlalchemy.orm.util import _class_to_mapper, _is_aliased_class

        if _is_aliased_class(mapper):
            searchfor = mapper
        else:
            searchfor = _class_to_mapper(mapper).base_mapper

        for ent in query._mapper_entities:
            if ent.path_entity is searchfor:
                return ent
        else:
            if raiseerr:
                raise sa_exc.ArgumentError("Can't find entity %s in Query.  Current list: %r"
                    % (searchfor, [str(m.path_entity) for m in query._entities]))
            else:
                return None

    def __getstate__(self):
        d = self.__dict__.copy()
        d['key'] = ret = []
        for token in util.to_list(self.key):
            if isinstance(token, PropComparator):
                ret.append((token.mapper.class_, token.key))
            else:
                ret.append(token)
        return d

    def __setstate__(self, state):
        ret = []
        for key in state['key']:
            if isinstance(key, tuple):
                cls, propkey = key
                ret.append(getattr(cls, propkey))
            else:
                ret.append(key)
        state['key'] = tuple(ret)
        self.__dict__ = state

    def __get_paths(self, query, raiseerr):
        path = None
        entity = None
        l = []

        # _current_path implies we're in a secondary load
        # with an existing path
        current_path = list(query._current_path)

        if self.mapper:
            entity = self.__find_entity(query, self.mapper, raiseerr)
            mapper = entity.mapper
            path_element = entity.path_entity

        for key in util.to_list(self.key):
            if isinstance(key, basestring):
                tokens = key.split('.')
            else:
                tokens = [key]
            for token in tokens:
                if isinstance(token, basestring):
                    if not entity:
                        entity = query._entity_zero()
                        path_element = entity.path_entity
                        mapper = entity.mapper
                    prop = mapper.get_property(token, resolve_synonyms=True, raiseerr=raiseerr)
                    key = token
                elif isinstance(token, PropComparator):
                    prop = token.property
                    if not entity:
                        entity = self.__find_entity(query, token.parententity, raiseerr)
                        if not entity:
                            return []
                        path_element = entity.path_entity
                    key = prop.key
                else:
                    raise sa_exc.ArgumentError("mapper option expects string key or list of attributes")

                if current_path and key == current_path[1]:
                    current_path = current_path[2:]
                    continue

                if prop is None:
                    return []

                path = build_path(path_element, prop.key, path)
                l.append(path)
                if getattr(token, '_of_type', None):
                    path_element = mapper = token._of_type
                else:
                    path_element = mapper = getattr(prop, 'mapper', None)
                if path_element:
                    path_element = path_element.base_mapper

        # if current_path tokens remain, then
        # we didn't have an exact path match.
        if current_path:
            return []

        return l

class AttributeExtension(object):
    """An event handler for individual attribute change events.

    AttributeExtension is assembled within the descriptors associated
    with a mapped class.

    """

    def append(self, state, value, initiator):
        """Receive a collection append event.

        The returned value will be used as the actual value to be
        appended.

        """
        return value

    def remove(self, state, value, initiator):
        """Receive a remove event.

        No return value is defined.

        """
        pass

    def set(self, state, value, oldvalue, initiator):
        """Receive a set event.

        The returned value will be used as the actual value to be
        set.

        """
        return value


class StrategizedOption(PropertyOption):
    """A MapperOption that affects which LoaderStrategy will be used
    for an operation by a StrategizedProperty.
    """

    def is_chained(self):
        return False

    def process_query_property(self, query, paths):
        if self.is_chained():
            for path in paths:
                query._attributes[("loaderstrategy", path)] = self.get_strategy_class()
        else:
            query._attributes[("loaderstrategy", paths[-1])] = self.get_strategy_class()

    def get_strategy_class(self):
        raise NotImplementedError()


class LoaderStrategy(object):
    """Describe the loading behavior of a StrategizedProperty object.

    The ``LoaderStrategy`` interacts with the querying process in three
    ways:

    * it controls the configuration of the ``InstrumentedAttribute``
      placed on a class to handle the behavior of the attribute.  this
      may involve setting up class-level callable functions to fire
      off a select operation when the attribute is first accessed
      (i.e. a lazy load)

    * it processes the ``QueryContext`` at statement construction time,
      where it can modify the SQL statement that is being produced.
      simple column attributes may add their represented column to the
      list of selected columns, *eager loading* properties may add
      ``LEFT OUTER JOIN`` clauses to the statement.

    * it processes the ``SelectionContext`` at row-processing time.  This
      includes straight population of attributes corresponding to rows,
      setting instance-level lazyloader callables on newly
      constructed instances, and appending child items to scalar/collection
      attributes in response to eagerly-loaded relations.
    """

    def __init__(self, parent):
        self.parent_property = parent
        self.is_class_level = False
        self.parent = self.parent_property.parent
        self.key = self.parent_property.key

    def init(self):
        raise NotImplementedError("LoaderStrategy")

    def init_class_attribute(self, mapper):
        pass

    def setup_query(self, context, entity, path, adapter, **kwargs):
        pass

    def create_row_processor(self, selectcontext, path, mapper, row, adapter):
        """Return row processing functions which fulfill the contract specified
        by MapperProperty.create_row_processor.

        StrategizedProperty delegates its create_row_processor method directly
        to this method.
        """

        raise NotImplementedError()

    def __str__(self):
        return str(self.parent_property)

    def debug_callable(self, fn, logger, announcement, logfn):
        if announcement:
            logger.debug(announcement)
        if logfn:
            def call(*args, **kwargs):
                logger.debug(logfn(*args, **kwargs))
                return fn(*args, **kwargs)
            return call
        else:
            return fn

class InstrumentationManager(object):
    """User-defined class instrumentation extension.

    The API for this class should be considered as semi-stable,
    and may change slightly with new releases.

    """

    # r4361 added a mandatory (cls) constructor to this interface.
    # given that, perhaps class_ should be dropped from all of these
    # signatures.

    def __init__(self, class_):
        pass

    def manage(self, class_, manager):
        setattr(class_, '_default_class_manager', manager)

    def dispose(self, class_, manager):
        delattr(class_, '_default_class_manager')

    def manager_getter(self, class_):
        def get(cls):
            return cls._default_class_manager
        return get

    def instrument_attribute(self, class_, key, inst):
        pass

    def post_configure_attribute(self, class_, key, inst):
        pass

    def install_descriptor(self, class_, key, inst):
        setattr(class_, key, inst)

    def uninstall_descriptor(self, class_, key):
        delattr(class_, key)

    def install_member(self, class_, key, implementation):
        setattr(class_, key, implementation)

    def uninstall_member(self, class_, key):
        delattr(class_, key)

    def instrument_collection_class(self, class_, key, collection_class):
        global collections
        if collections is None:
            from sqlalchemy.orm import collections
        return collections.prepare_instrumentation(collection_class)

    def get_instance_dict(self, class_, instance):
        return instance.__dict__

    def initialize_instance_dict(self, class_, instance):
        pass

    def install_state(self, class_, instance, state):
        setattr(instance, '_default_state', state)

    def remove_state(self, class_, instance):
        delattr(instance, '_default_state', state)

    def state_getter(self, class_):
        return lambda instance: getattr(instance, '_default_state')

    def dict_getter(self, class_):
        return lambda inst: self.get_instance_dict(class_, inst)
